"""Exercise the patched scheduler's actual queue methods without a Vulkan device."""
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).resolve()
code = (source / 'src/video_core/renderer_vulkan/vk_scheduler.cpp').read_text()

def method(name):
    start = code.index(f'void Scheduler::{name}(')
    opening = code.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (code[end] == '{') - (code[end] == '}')
        end += 1
    return code[start:end]

harness = r'''
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <iostream>
#include <memory>
#include <mutex>
#include <queue>
#include <thread>
#include <utility>
#include <vector>
namespace Common {
enum class ThreadPriority { Critical };
void SetCurrentThreadName(const char*) {}
void SetCurrentThreadPriority(ThreadPriority) {}
void SetCurrentThreadToPerformanceCores() {}
}
class Scheduler {
    struct CommandChunk {
        Scheduler* owner;
        std::vector<unsigned> commands;
        bool Empty() const { return commands.empty(); }
        bool HasSubmit() const { return false; }
        void ExecuteAll(int, int) {
            for (auto id : commands) {
                assert(id == owner->executed.load());
                ++owner->executed;
                if (id % 61 == 0) std::this_thread::yield();
            }
        }
    };
    std::unique_ptr<CommandChunk> chunk;
    std::queue<std::unique_ptr<CommandChunk>> work_queue;
    std::vector<std::unique_ptr<CommandChunk>> chunk_reserve;
    std::mutex execution_mutex, reserve_mutex, queue_mutex;
    std::condition_variable_any event_cv;
    bool worker_waiting = false;
    uint32_t drain_waiters = 0;
    std::jthread worker_thread;
    int current_cmdbuf = 0, current_upload_cmdbuf = 0;
    void AcquireNewChunk() { chunk = std::make_unique<CommandChunk>(this); }
    void AllocateWorkerCommandBuffer() {}
    void WorkerThread(std::stop_token);
public:
    std::atomic<unsigned> executed{0};
    Scheduler() {
        AcquireNewChunk();
        worker_thread = std::jthread([this](std::stop_token s) { WorkerThread(s); });
    }
    ~Scheduler() {
        worker_thread.request_stop();
        worker_thread.join();
    }
    void WaitWorker();
    void DispatchWork();
    void Add(unsigned id) { chunk->commands.push_back(id); }
};
'''
harness += '\n'.join(method(name) for name in ['WaitWorker', 'DispatchWork', 'WorkerThread'])
harness += r'''
int main() {
    for (unsigned round = 0; round < 20; ++round) {
        Scheduler s;
        s.WaitWorker();
        for (unsigned i = 0; i < 10000; ++i) {
            s.Add(i);
            s.DispatchWork();
            if (i % 127 == 0) {
                s.WaitWorker();
                assert(s.executed == i + 1);
            }
            if (i % 503 == 0) std::this_thread::sleep_for(std::chrono::microseconds(50));
        }
        s.WaitWorker();
        assert(s.executed == 10000);
    }
    for (int i = 0; i < 200; ++i) {
        Scheduler s;
        if (i % 2) std::this_thread::sleep_for(std::chrono::microseconds(50));
    }
    std::cout << "PASS: FIFO execution, queue drain, repeated idle wakeups, and stop while idle.\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / 'worker.cpp'
    binary = Path(directory) / 'worker'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++20', '-O2', '-pthread', str(cpp), '-o', str(binary)], check=True, timeout=60)
    subprocess.run([str(binary)], check=True, timeout=60)
