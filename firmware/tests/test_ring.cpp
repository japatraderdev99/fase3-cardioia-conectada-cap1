#include "../RingBuffer.h"
#include <cassert>
#include <iostream>
struct Sample { uint32_t seq; };
int main() {
  RingBuffer<Sample, 3> q; Sample s{};
  assert(!q.peek(s)); assert(!q.popIfSequence(0));
  for (uint32_t i=1; i<=3; ++i) q.push({i});
  assert(q.size()==3 && q.dropped()==0);
  q.push({4}); assert(q.dropped()==1 && q.peek(s) && s.seq==2);
  // In-flight oldest eviction must not pop a newer record.
  assert(!q.popIfSequence(1)); assert(q.size()==3);
  assert(q.popIfSequence(2)); assert(q.peek(s) && s.seq==3);
  q.push({5}); q.push({6}); assert(q.dropped()==2);
  for (uint32_t i=4; i<=6; ++i) { assert(q.peek(s) && s.seq==i); assert(q.popIfSequence(i)); }
  assert(q.size()==0);
  RingBuffer<Sample, 2000> full;
  for(uint32_t i=1; i<=10000; ++i) full.push({i});
  assert(full.size()==2000 && full.dropped()==8000);
  for(uint32_t i=8001; i<=10000; ++i) { assert(full.peek(s) && s.seq==i); assert(full.popIfSequence(i)); }
  std::cout << "PASS empty, FIFO, wraparound, capacity=2000, overflow=8000, in-flight eviction guard\n";
}
