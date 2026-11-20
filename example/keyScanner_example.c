/* SPDX-License-Identifier: MIT */
/*
 * KeyScanner 使用示例（本文件仅作参考，未编入工程）
 *
 * 场景：3 个低电平有效的按键
 *   1) 自复位按键：按一下触发一次（取按下沿事件）
 *   2) 拨动开关：按稳定电平决定状态
 *   3) 长按：按住超过 1 秒执行一次动作（用 isLongPressed + 按下沿事件做边沿触发）
 */

#include "KeyScanner.h"
#include "AI8051U.h"

/* ---- 1) 接线层：每个键一个读取回调（返回 1 = 按下/闭合） ---- */
static uint8_t key_reset_is_pressed(void) { return (0 == P20) ? 1 : 0; }
static uint8_t key_mode0_is_pressed(void) { return (0 == P21) ? 1 : 0; }
static uint8_t key_mode1_is_pressed(void) { return (0 == P22) ? 1 : 0; }

static KeyScanner* keyReset;
static KeyScanner* keyMode0;
static KeyScanner* keyMode1;

void keyScanner_example_init(void) {
    /* 引脚配置为准双向（具体到你的项目：P2M1/P2M0 对应位清 0，并把引脚写 1） */
    P2M1 &= ~0x07;
    P2M0 &= ~0x07;
    P20 = 1;
    P21 = 1;
    P22 = 1;

    /* ---- 2) 注册：每个键一个句柄 ---- */
    keyReset = keyScanner_init(key_reset_is_pressed);
    keyMode0 = keyScanner_init(key_mode0_is_pressed);
    keyMode1 = keyScanner_init(key_mode1_is_pressed);

    /* ---- 3) 启动：立即采样一次作为初始状态，上电即按住的键不会产生假事件 ---- */
    keyScanner_start(keyReset);
    keyScanner_start(keyMode0);
    keyScanner_start(keyMode1);

    /* 拨动开关这种“拨到哪算哪”的键，去抖可以给得大一点（例如 3 拍 = 30ms） */
    keyScanner_setDebounceCnt(keyMode1, 3);
}

/* 每 10ms 调用一次（与 userKeyScannerCfg.h 里的 KEY_SCANNER_CYCLE_MS 对应） */
void keyScanner_example_ticks(void) {
    keyScanner_scan();
}

/* 主循环里查询 */
void keyScanner_example_app(void) {
    static uint8_t longDone = 0;   /* 本次按下是否已执行过长按动作 */

    /* 自复位按键：按一下触发一次（事件读取后自动清除，所以只读一次） */
    if (keyScanner_getPressedEvent(keyReset)) {
        longDone = 0;              /* 新的一次按下，重新允许长按 */
        /* 短按动作 */
    }

    /* 拨动开关：看稳定电平 */
    if (keyScanner_isPressed(keyMode0)) {
        /* 开关在闭合位置 */
    }

    /* 长按：按住到 1 秒的那一拍执行一次，用标志位保证“按一次只执行一次” */
    if (keyScanner_isLongPressed(keyReset, 1000) && 0 == longDone) {
        longDone = 1;
        /* 长按动作 */
    }

    /* 按住时长的原始值（毫秒） */
    (void)keyScanner_getHoldMs(keyMode1);
}
