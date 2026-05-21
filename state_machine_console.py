import time
import threading
import os
import sys

try:
    import msvcrt
except ImportError:
    msvcrt = None


class StateMachine:
    def __init__(self):
        self.state = 'Idle'
        self.previous_state = 'Idle'
        self.running = True
        self.event_log = []
        self.lock = threading.Lock()

    def transition(self, event):
        with self.lock:
            old_state = self.state
            if self.state == 'Idle':
                if event == 'w':
                    self.state = 'Walking'
                elif event == 'r':
                    self.state = 'Running'
                elif event == 'j':
                    self.state = 'Jumping'
                elif event == 'p':
                    self.previous_state = self.state
                    self.state = 'Paused'
            elif self.state == 'Walking':
                if event == 's':
                    self.state = 'Idle'
                elif event == 'r':
                    self.state = 'Running'
                elif event == 'j':
                    self.state = 'Jumping'
                elif event == 'p':
                    self.previous_state = self.state
                    self.state = 'Paused'
            elif self.state == 'Running':
                if event == 's':
                    self.state = 'Idle'
                elif event == 'w':
                    self.state = 'Walking'
                elif event == 'j':
                    self.state = 'Jumping'
                elif event == 'p':
                    self.previous_state = self.state
                    self.state = 'Paused'
            elif self.state == 'Jumping':
                if event == 'l':
                    self.state = 'Landing'
                elif event == 'p':
                    self.previous_state = self.state
                    self.state = 'Paused'
            elif self.state == 'Landing':
                if event == 's':
                    self.state = 'Idle'
                elif event == 'w':
                    self.state = 'Walking'
                elif event == 'r':
                    self.state = 'Running'
                elif event == 'p':
                    self.previous_state = self.state
                    self.state = 'Paused'
            elif self.state == 'Paused':
                if event == 'u':
                    self.state = self.previous_state
                elif event == 's':
                    self.state = 'Idle'
            self.event_log.append((time.time(), event, old_state, self.state))

    def stop(self):
        with self.lock:
            self.running = False

    def get_state(self):
        with self.lock:
            return self.state

    def is_running(self):
        with self.lock:
            return self.running


def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def print_help():
    print('콘솔 상태 머신 프로그램')
    print('키를 눌러 상태를 전환하세요:')
    print('  w - 걷기 (Walking)')
    print('  r - 달리기 (Running)')
    print('  j - 점프 (Jumping)')
    print('  l - 착지 (Landing)')
    print('  s - 정지 / Idle')
    print('  p - 일시정지 (Pause)')
    print('  u - 일시정지 해제 (Unpause)')
    print('  q - 종료 (Quit)')
    print('  h - 도움말 다시 보기')
    print('')


def read_key():
    if msvcrt:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b'\x00', b'\xe0'):
                    msvcrt.getch()
                    continue
                try:
                    return key.decode('utf-8').lower()
                except UnicodeDecodeError:
                    continue
            time.sleep(0.01)
    else:
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                return ch.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            return sys.stdin.readline().strip().lower()


def main():
    state_machine = StateMachine()
    clear_console()
    print_help()
    print('상태 머신 실행 중... 키 입력을 기다립니다.')

    while state_machine.is_running():
        current_state = state_machine.get_state()
        print(f'현재 상태: {current_state}')
        key = read_key()
        if key == 'q':
            state_machine.stop()
            break
        if key == 'h':
            clear_console()
            print_help()
            continue
        if key in ('w', 'r', 'j', 'l', 's', 'p', 'u'):
            state_machine.transition(key)
            clear_console()
            print_help()
        else:
            clear_console()
            print('알 수 없는 키입니다:', repr(key))
            print_help()

    clear_console()
    print('프로그램을 종료합니다. 상태 전환 로그:')
    for timestamp, event, old_state, new_state in state_machine.event_log:
        local_time = time.strftime('%H:%M:%S', time.localtime(timestamp))
        print(f'[{local_time}] {event} : {old_state} -> {new_state}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n사용자에 의해 중단되었습니다.')
