/* SPDX-License-Identifier: MIT */
#include "KeyScanner.h"

/*
 * KeyScanner —— 通用按键扫描库（实现）
 *
 * 结构：静态池 keyPool[KEY_SCANNER_NUM]，每个槽位一个句柄；
 *       扫描按槽位顺序遍历，不做链表，因此 start / stop 只写一个单字节标志，
 *       不存在“中断里正遍历、主程序同时摘链”的问题。
 * 状态机：每拍读一次原始状态 raw，与稳定状态 stable 比较：
 *         - 一致：去抖计数清零；
 *         - 不一致：计数累加，累加到 KEY_SCANNER_DEBOUNCE_TICKS 次才认定翻转，并按方向置边沿事件、复位/启动按住计数。
 */

#define KEY_SCANNER_CNT_MAX   0xFFFFu
#define KEY_SCANNER_DEBOUNCE_TICKS  ((uint8_t)KEY_SCANNER_CNT_OF_MS(KEY_SCANNER_DEBOUNCE_MS))   /* 全局一套，编译期常量 */

static KeyScanner KEY_SCANNER_MEM_ATTR keyPool[KEY_SCANNER_NUM];
static uint16_t keyUsedCount;

/* ---- 空对象：read 永远可调用 ------------------------------------------------------------
 * 函数指针与通用空指针宽度不保证一致（C251 上 code 指针 2 字节、通用空指针 3 字节），
 * 直接把通用空指针赋给函数指针会截断并触发 C151 告警。改用“空实现”兜底后，
 * 句柄里不存在空函数指针，扫描时不必逐拍判空。 */
static uint8_t keyScanner_neverPressed(void){
    return 0;
}

static void keyScanner_sample(KeyScanner* handle){
    handle->stable  = (handle->is_pressed)() ? 1u : 0u;
    handle->cnt     = 0;
    handle->holdCnt = (handle->stable) ? 1u : 0u;
    handle->evtPress   = 0;
    handle->evtRelease = 0;
}

/* 从静态池分配一个句柄：is_pressed 传 0 时换成空实现（永远不按下）；去抖时间统一取配置宏 */
KeyScanner* keyScanner_init(io_is_pressed_func is_pressed){
    uint16_t i;

    for(i = 0; i < (uint16_t)KEY_SCANNER_NUM; i++){
        KeyScanner* handle = &keyPool[i];
        if(handle->inUse) continue;

        /* 先填内容、最后再置 inUse：扫描看到 inUse == 1 时，其余字段已经是完整的 */
        handle->is_pressed = is_pressed ? is_pressed : keyScanner_neverPressed;
        handle->stable    = 0;
        handle->cnt       = 0;
        handle->evtPress  = 0;
        handle->evtRelease = 0;
        handle->holdCnt   = 0;
        handle->scanning  = 0;
        handle->inUse     = 1;

        keyUsedCount++;
        return handle;
    }

    return 0;   /* 池已用尽 */
}

/* 归还槽位：先退出扫描，再清空；inUse 最后清，理由同上 */
void keyScanner_deinit(KeyScanner* handle){
    if(0 == handle) return;

    handle->scanning   = 0;
    handle->stable     = 0;
    handle->cnt        = 0;
    handle->evtPress   = 0;
    handle->evtRelease = 0;
    handle->holdCnt    = 0;
    handle->is_pressed       = keyScanner_neverPressed;
    handle->inUse      = 0;

    if(keyUsedCount > 0) keyUsedCount--;
}

/* 纳入扫描：立即采样一次，避免上电即按住的键被当成一次事件 */
void keyScanner_start(KeyScanner* handle){
    if(0 == handle || 0 == handle->inUse) return;

    keyScanner_sample(handle);
    handle->scanning = 1;
}

/* 退出扫描：保持最后的稳定状态，不再产生事件 */
void keyScanner_stop(KeyScanner* handle){
    if(0 == handle) return;

    handle->scanning = 0;
    handle->cnt      = 0;
}

/* 节拍：逐槽位推进。未分配或未 start 的槽位直接跳过。 */
void keyScanner_scan(void){
    uint16_t i;

    for(i = 0; i < (uint16_t)KEY_SCANNER_NUM; i++){
        KeyScanner* handle = &keyPool[i];
        uint8_t  raw;

        if(0 == handle->inUse || 0 == handle->scanning) continue;

        raw = (handle->is_pressed)() ? 1u : 0u;

        if(raw == handle->stable){
            handle->cnt = 0;                    /* 抖动未持续，计数清零 */
            continue;
        }

        handle->cnt++;
        if(handle->cnt < KEY_SCANNER_DEBOUNCE_TICKS) continue;   /* 还没连续够，继续等 */

        /* 认定状态翻转 */
        handle->stable = raw;
        handle->cnt    = 0;

        if(raw){
            handle->evtPress = 1;               /* 松开 → 按下 */
            handle->holdCnt  = 0;               /* 从本拍起由下面的循环开始累计 */
        }else{
            handle->evtRelease = 1;             /* 按下 → 松开 */
            handle->holdCnt    = 0;
        }
    }

    /* 按住计时只在“稳定按下”期间累计，与去抖状态同步推进 */
    for(i = 0; i < (uint16_t)KEY_SCANNER_NUM; i++){
        KeyScanner* handle = &keyPool[i];

        if(0 == handle->inUse || 0 == handle->scanning) continue;
        if(0 == handle->stable) continue;

        if(handle->holdCnt < KEY_SCANNER_CNT_MAX) handle->holdCnt++;
    }
}

uint8_t keyScanner_isPressed(KeyScanner* handle){
    if(0 == handle || 0 == handle->inUse) return 0;
    return handle->stable;
}

uint8_t keyScanner_isReleased(KeyScanner* handle){
    if(0 == handle || 0 == handle->inUse) return 1;
    return (handle->stable) ? 0u : 1u;
}

/* 事件读取后自动清除 */
uint8_t keyScanner_getPressedEvent(KeyScanner* handle){
    uint8_t evt;

    if(0 == handle || 0 == handle->inUse) return 0;

    evt = handle->evtPress;
    handle->evtPress = 0;
    return evt;
}

uint8_t keyScanner_getReleasedEvent(KeyScanner* handle){
    uint8_t evt;

    if(0 == handle || 0 == handle->inUse) return 0;

    evt = handle->evtRelease;
    handle->evtRelease = 0;
    return evt;
}

void keyScanner_clearEvents(KeyScanner* handle){
    if(0 == handle || 0 == handle->inUse) return;

    handle->evtPress   = 0;
    handle->evtRelease = 0;
}

/* 按住时长：拍数 × 周期，饱和到 65535 毫秒（避免长按很久后回绕） */
uint16_t keyScanner_getHoldMs(KeyScanner* handle){
    uint32_t ms;

    if(0 == handle || 0 == handle->inUse) return 0;

    ms = (uint32_t)handle->holdCnt * (uint32_t)KEY_SCANNER_CYCLE_MS;
    if(ms > 65535UL) return 0xFFFFu;

    return (uint16_t)ms;
}

uint8_t keyScanner_isLongPressed(KeyScanner* handle, uint16_t holdMs){
    if(0 == handle || 0 == handle->inUse) return 0;
    if(0 == handle->stable) return 0;

    return (keyScanner_getHoldMs(handle) >= holdMs) ? 1u : 0u;
}

uint16_t keyScanner_getUsedCount(void){
    return keyUsedCount;
}

uint16_t keyScanner_getCapacity(void){
    return (uint16_t)KEY_SCANNER_NUM;
}
