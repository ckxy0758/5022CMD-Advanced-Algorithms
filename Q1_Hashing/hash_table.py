"""
A generic hash table using Open Addressing with Linear Probing.

The table knows nothing about pharmacy products: keys can be any value that
can be converted to a string and compared with ==, and values can be any
object. This keeps the data structure reusable in other programs.
"""

from enum import Enum


class SlotState(Enum):
    """The three possible states of a slot in an open-addressing table."""
    EMPTY = 0      # never used - a search can stop here
    OCCUPIED = 1   # currently holds a key-value pair
    DELETED = 2    # held a pair that was removed (tombstone) - a search must continue past it


class _Slot:
    """One slot (bucket) of the hash table.

    Each slot stores at most one key-value pair, because open addressing
    resolves collisions by moving to another slot instead of chaining.
    """
    __slots__ = ("key", "value", "state")   # fixed attributes: less memory per slot

    def __init__(self):
        self.key = None
        self.value = None
        self.state = SlotState.EMPTY

    def __repr__(self):
        return f"_Slot(key={self.key!r}, state={self.state.name})"


class DuplicateKeyError(KeyError):
    """Raised when inserting a key that already exists in the table."""


class HashTable:
    """Hash table with open addressing and linear probing.

    Probe sequence for a key k:  h(k), h(k)+1, h(k)+2, ...  (mod capacity)
    """

    DEFAULT_CAPACITY = 31          # prime number: spreads keys more evenly under modulo
    DEFAULT_MAX_LOAD_FACTOR = 0.7  # resize before probe chains get long

    def __init__(self, capacity=DEFAULT_CAPACITY,
                 max_load_factor=DEFAULT_MAX_LOAD_FACTOR,
                 hash_function=None):
        """
        capacity        : initial number of slots (rounded up to a prime).
        max_load_factor : resize when size / capacity would exceed this.
                          Pass None to disable resizing (fixed-size table).
        hash_function   : optional custom function f(key, capacity) -> index.
                          Defaults to the polynomial string hash below.
        """
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if max_load_factor is not None and not 0 < max_load_factor <= 1:
            raise ValueError("max_load_factor must be in (0, 1]")

        self._capacity = self._next_prime(capacity)
        self._max_load_factor = max_load_factor
        self._hash_function = hash_function or self._polynomial_hash
        self._slots = [_Slot() for _ in range(self._capacity)]
        self._size = 0          # number of OCCUPIED slots
        self._tombstones = 0    # number of DELETED slots
        self.collisions = 0     # insertions whose home slot was already taken

    # ------------------------------------------------------------------ #
    # Hashing helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _polynomial_hash(key, capacity):
        """Polynomial rolling hash with a multiplicative mixing step.

        Step 1 - polynomial hash over the characters of str(key):
                 h = c0*31^(n-1) + c1*31^(n-2) + ... + c(n-1)   (kept to 32 bits)
        Step 2 - mix the bits (Knuth's multiplicative method), so keys that
                 differ only slightly (P1001, P1002, ...) are scattered across
                 the table instead of landing in neighbouring slots. Without
                 this, sequential IDs formed long clusters (primary clustering).
        Step 3 - reduce to a slot index with mod capacity.

        Written by hand instead of using Python's built-in hash(), because
        hash() of a string is randomised on every run, which would make slot
        numbers change between runs. Runs in O(L), L = length of the key.
        """
        h = 0
        for ch in str(key):
            h = (h * 31 + ord(ch)) & 0xFFFFFFFF   # & 0xFFFFFFFF keeps h within 32 bits
        h = (h * 2654435761) & 0xFFFFFFFF          # Knuth's constant (about 2^32 / golden ratio)
        h ^= h >> 16                               # fold high bits into the low bits
        return h % capacity

    @staticmethod
    def _is_prime(n):
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True

    @classmethod
    def _next_prime(cls, n):
        while not cls._is_prime(n):
            n += 1
        return n

    def _home_index(self, key):
        return self._hash_function(key, self._capacity) % self._capacity

    # ------------------------------------------------------------------ #
    # Core probing routine
    # ------------------------------------------------------------------ #
    def _probe(self, key):
        """Walk the probe sequence for key.

        Returns (found_index, first_free_index, probes):
          found_index      - slot holding key, or None if key is absent
          first_free_index - first DELETED or EMPTY slot seen (where an insert
                             should go), or None if the table has no free slot
          probes           - number of slots examined
        """
        index = self._home_index(key)
        first_free = None
        probes = 0

        for _ in range(self._capacity):          # at most one full lap
            slot = self._slots[index]
            probes += 1

            if slot.state is SlotState.EMPTY:
                # key cannot be further along: an insert would have used this slot
                if first_free is None:
                    first_free = index
                return None, first_free, probes

            if slot.state is SlotState.DELETED:
                if first_free is None:
                    first_free = index           # remember, but keep searching
            elif slot.key == key:                # OCCUPIED and matching
                return index, first_free, probes

            index = (index + 1) % self._capacity  # linear probing step

        return None, first_free, probes          # full lap, key absent

    # ------------------------------------------------------------------ #
    # Public operations
    # ------------------------------------------------------------------ #
    def insert(self, key, value):
        """Insert a new key-value pair and return the slot index used.

        Raises DuplicateKeyError if the key already exists (use update()).
        """
        if self._max_load_factor is not None and \
                (self._size + self._tombstones + 1) / self._capacity > self._max_load_factor:
            self._resize(self._capacity * 2)

        found, free, _ = self._probe(key)
        if found is not None:
            raise DuplicateKeyError(f"key {key!r} already exists")
        if free is None:
            raise OverflowError("hash table is full")

        if free != self._home_index(key):
            self.collisions += 1

        slot = self._slots[free]
        if slot.state is SlotState.DELETED:
            self._tombstones -= 1
        slot.key, slot.value, slot.state = key, value, SlotState.OCCUPIED
        self._size += 1
        return free

    def search(self, key):
        """Return the value stored for key, or None if the key is absent."""
        found, _, _ = self._probe(key)
        return None if found is None else self._slots[found].value

    def search_with_stats(self, key):
        """Return (value, slot_index, probes). value and slot_index are None if absent."""
        found, _, probes = self._probe(key)
        if found is None:
            return None, None, probes
        return self._slots[found].value, found, probes

    def update(self, key, value):
        """Replace the value of an existing key. Raises KeyError if absent."""
        found, _, _ = self._probe(key)
        if found is None:
            raise KeyError(key)
        self._slots[found].value = value
        return found

    def delete(self, key):
        """Remove key and return its value. Raises KeyError if absent.

        The slot becomes a tombstone (DELETED), not EMPTY, so that searches
        for keys placed after it in the same probe chain still succeed.
        """
        found, _, _ = self._probe(key)
        if found is None:
            raise KeyError(key)
        slot = self._slots[found]
        value = slot.value
        slot.key, slot.value, slot.state = None, None, SlotState.DELETED
        self._size -= 1
        self._tombstones += 1
        return value

    def _resize(self, new_capacity):
        """Rehash every occupied pair into a larger table (drops tombstones)."""
        old_slots = self._slots
        self._capacity = self._next_prime(new_capacity)
        self._slots = [_Slot() for _ in range(self._capacity)]
        self._size = 0
        self._tombstones = 0
        self.collisions = 0
        for slot in old_slots:
            if slot.state is SlotState.OCCUPIED:
                # same placement logic as insert(), without the resize check
                _, free, _ = self._probe(slot.key)
                if free != self._home_index(slot.key):
                    self.collisions += 1
                new = self._slots[free]
                new.key, new.value, new.state = slot.key, slot.value, SlotState.OCCUPIED
                self._size += 1

    # ------------------------------------------------------------------ #
    # Inspection helpers
    # ------------------------------------------------------------------ #
    @property
    def capacity(self):
        return self._capacity

    def home_slot(self, key):
        """Slot the key hashes to before any probing (its 'home' slot)."""
        return self._home_index(key)

    @property
    def load_factor(self):
        return self._size / self._capacity

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self._probe(key)[0] is not None

    def items(self):
        """Yield (slot_index, key, value) for every occupied slot, in slot order."""
        for i, slot in enumerate(self._slots):
            if slot.state is SlotState.OCCUPIED:
                yield i, slot.key, slot.value

    def slot_states(self):
        """Return the state of every slot (useful for displaying the table)."""
        return [slot.state for slot in self._slots]