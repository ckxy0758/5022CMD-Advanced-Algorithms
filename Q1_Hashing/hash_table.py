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
    DEFAULT_MAX_LOAD_FACTOR = 0.5  # resize before probe chains get long
    HASH_BASE = 37                 # prime base for Horner's method (must differ from capacity)

    def __init__(self, capacity=DEFAULT_CAPACITY,
                 max_load_factor=DEFAULT_MAX_LOAD_FACTOR,
                 hash_function=None):
        """
        capacity        : initial number of slots (rounded up to a prime).
        max_load_factor : resize when size / capacity would exceed this.
                          Pass None to disable resizing (fixed-size table).
        hash_function   : optional custom function f(key, capacity) -> index.
                          Defaults to _default_hash (division / Horner).
        """
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if max_load_factor is not None and not 0 < max_load_factor <= 1:
            raise ValueError("max_load_factor must be in (0, 1]")

        self._capacity = self._next_prime(capacity)
        self._max_load_factor = max_load_factor
        self._hash_function = hash_function or self._default_hash
        self._slots = [_Slot() for _ in range(self._capacity)]
        self._size = 0          # number of OCCUPIED slots
        self._tombstones = 0    # number of DELETED slots
        self.collisions = 0     # insertions whose home slot was already taken

    # ------------------------------------------------------------------ #
    # Hashing helpers
    # ------------------------------------------------------------------ #
    @classmethod
    def _default_hash(cls, key, capacity):
        """Choose the hash method by key type.

        Integer keys use the division method; every other key is converted
        to a string and hashed with Horner's method.
        """
        if isinstance(key, int):
            return cls._division_hash(key, capacity)
        return cls._polynomial_hash(str(key), capacity)

    @staticmethod
    def _division_hash(key, capacity):
        """Division method: h(k) = k mod capacity.  O(1)."""
        return key % capacity

    @classmethod
    def _polynomial_hash(cls, text, capacity):
        """Horner's method for strings.

        Treats the string as a polynomial in base B = HASH_BASE:
            h = c0*B^(n-1) + c1*B^(n-2) + ... + c(n-1)   (mod capacity)
        Horner's rule evaluates it with one multiply and one add per
        character, taking mod capacity at every step so h stays small.

        B must not equal the (prime) capacity: if it did, B^k mod capacity
        would be 0 and only the last character would affect the slot.
        _next_prime() therefore never returns HASH_BASE as a capacity.

        Written by hand instead of using Python's built-in hash(), because
        hash() of a string is randomised on every run, which would make slot
        numbers change between runs. Runs in O(L), L = length of the key.
        """
        h = 0
        for ch in text:
            h = (h * cls.HASH_BASE + ord(ch)) % capacity
        return h

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
        """Smallest prime >= n, skipping HASH_BASE (see _polynomial_hash)."""
        while not cls._is_prime(n) or n == cls.HASH_BASE:
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
        # 1. Reject duplicates first, so a failed insert never changes the table.
        found, free, _ = self._probe(key)
        if found is not None:
            raise DuplicateKeyError(f"key {key!r} already exists")

        # 2. Only a genuinely new key may trigger a resize.
        if self._max_load_factor is not None and \
                (self._size + self._tombstones + 1) / self._capacity > self._max_load_factor:
            self._resize(self._capacity * 2)
            _, free, _ = self._probe(key)   # slots moved: find the new free slot

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