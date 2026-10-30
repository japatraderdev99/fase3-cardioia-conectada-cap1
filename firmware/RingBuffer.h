#pragma once
#include <stddef.h>
#include <stdint.h>
// Caller provides synchronization. Overload drops oldest, never blocks collection.
template <typename T, size_t N> class RingBuffer {
  static_assert(N > 0, "capacity must be positive");
  T values_[N]{};
  size_t head_ = 0, count_ = 0;
  uint32_t dropped_ = 0;
public:
  void push(const T &value) {
    if (count_ == N) { head_ = (head_ + 1) % N; --count_; ++dropped_; }
    values_[(head_ + count_) % N] = value; ++count_;
  }
  bool peek(T &value) const { if (!count_) return false; value = values_[head_]; return true; }
  // Network may finish after oldest was evicted: never remove a different sample.
  bool popIfSequence(uint32_t seq) {
    if (!count_ || values_[head_].seq != seq) return false;
    head_ = (head_ + 1) % N; --count_; return true;
  }
  size_t size() const { return count_; }
  uint32_t dropped() const { return dropped_; }
};
