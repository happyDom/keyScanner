/* SPDX-License-Identifier: MIT */
#ifndef KEY_SCANNER_a61d2c4e_8f37_4a9b_b0d2_5c7e9f1083ab
#define KEY_SCANNER_a61d2c4e_8f37_4a9b_b0d2_5c7e9f1083ab

#include <stdint.h>

/* KeyScanner —— 通用按键扫描库
 *
 * 设计目标：把“去抖 + 状态/边沿事件生成”这段逻辑做成通用模块，
 * 不关心按键接在哪个引脚、是高电平有效还是低电平有效，也不关心按的是自复位按键还是拨动开关。
 *
 *   - 每个按键一个句柄（一个键 = 一个注册项），句柄由库内静态内存池分配，
 *     池的大小由项目侧的 KEY_SCANNER_NUM 决定，不使用动态内存；
 *     按键个数在硬件上是确定的，宏一次写死即可，句柄分配后常驻、无释放与用量查询接口；
 *   - 按键的原始电平由调用方通过 io_is_pressed_func 提供，返回 1 表示“按下/闭合”（动作态），
 *     因此低电平有效的按键要写成 return (0 == P20) ? 1 : 0;（引脚读到 0 才算按下）；
 *   - 库不自己计时，由调用方按固定周期调用 keyScanner_scan()，该周期即“一拍”；
 *     去抖时间统一由项目配置里的 KEY_SCANNER_DEBOUNCE_MS 决定（毫秒），库内按扫描周期折算成拍，
 *     所以调用方不必关心拍数；
 *   - 对外提供三类查询：稳定状态（isPressed / isReleased）、
 *     边沿事件（getPressedEvent / getReleasedEvent，读取后自动清除）、按住时长（getHoldMs）。
 *
 * 两个设计选择（有意为之）：
 *   1) 没有调度链表：句柄在内存池里的位置固定，扫描就是按槽位顺序遍历一遍，
 *      因此 start / stop 只是写一个单字节标志，立刻生效，不存在“中断里正遍历、主程序同时改结构”的问题；
 *   2) 事件是“粘滞标志 + 读后清除”，不排队。同一个键在两次读取之间发生的多次翻转
 *      只会留下最后一次事件的痕迹，按键场景下这样足够，也省 RAM。
 *
 * 请认真阅读以下关于 userKeyScannerCfg.h 的使用说明：
 * 1、按键数量：KEY_SCANNER_NUM 决定静态内存池大小（= KEY_SCANNER_NUM * sizeof(KeyScanner)）。
 *     请在项目里创建 userKeyScannerCfg.h（可照抄本库 cfg/ 目录下的 userKeyScannerCfg.h.sample），
 *     并在其中定义 KEY_SCANNER_NUM。
 * 2、扫描周期：KEY_SCANNER_CYCLE_MS 必须与调用 keyScanner_scan() 的实际周期一致，
 *     库内的去抖次数与毫秒换算（getHoldMs）都以它为唯一依据。
 * 3、可选：KEY_SCANNER_MEM_ATTR 指定内存池存放区（data/idata/xdata/pdata）。
 */

#include "userKeyScannerCfg.h"

#ifndef KEY_SCANNER_MEM_ATTR
#define KEY_SCANNER_MEM_ATTR
#endif

#ifndef KEY_SCANNER_NUM
#error "please #define KEY_SCANNER_NUM          //in userKeyScannerCfg.h"
#elif KEY_SCANNER_NUM <= 0
#error "KEY_SCANNER_NUM must be greater than 0!"
#endif

#ifndef KEY_SCANNER_CYCLE_MS
#error "please #define KEY_SCANNER_CYCLE_MS     //in userKeyScannerCfg.h"
#elif KEY_SCANNER_CYCLE_MS <= 0
#error "KEY_SCANNER_CYCLE_MS must be greater than 0!"
#endif

#ifndef KEY_SCANNER_DEBOUNCE_MS
#define KEY_SCANNER_DEBOUNCE_MS    20u   /* 默认去抖时间（毫秒），库内按扫描周期折算成拍 */
#endif

/* 毫秒 → 拍换算（向上取整）：保证非 0 的毫秒数至少折算为 1 拍，0 毫秒仍为 0 拍。
 * 对外的时长口径一律是毫秒，库内自己折算成“拍”，调用方不需要关心拍数，
 * 也就不会把自己的应用节拍与扫描节拍混为一谈。 */
#ifndef KEY_SCANNER_CNT_OF_MS
#define KEY_SCANNER_CNT_OF_MS(ms)  ((uint16_t)(((uint32_t)(ms) + (KEY_SCANNER_CYCLE_MS - 1u)) / KEY_SCANNER_CYCLE_MS))
#endif

/* 使用注意（集成到项目时踩过或容易踩的点）
 * 1、扫描函数通常放在定时器中断里（节拍稳定），此时按键状态与事件在中断里更新、
 *     在主循环里读取。涉及的都是单字节/单字写入，8051 上不会被读成“半个值”；
 *     但“读事件 → 清事件”之间若正好又被中断置位，这一次事件会丢。
 *     需要严格不丢事件时，读清动作放在同一处临界区（EA=0 / EA=1）里，或改用计数方式。
 * 2、start 时会立即采样一次作为初始稳定状态，所以“上电那一刻按住的键”不会产生一次假事件；
 *     但这也意味着 keyScanner_start 之后即认为状态有效，无需再等去抖。
 * 3、isPressed 读的是去抖后的稳定状态；要对照万用表/示波器看引脚电平，用你的 read 回调自己读。
 * 4、按住时长 getHoldMs 只在“稳定按下”期间累计，松开即清零；
 *     它是查询值，不是事件，长按判定由调用方用 isLongPressed 或自己比较。
 * 5、句柄字段由库内维护，调用方不要改写（尤其 inUse / scanning 两个字节会破坏分配与扫描）。
 * 6、事件读取后自动清除，多个任务/多处代码都要用同一个键时，请指定唯一一处负责取事件。
 */

/* 读取按键原始状态的回调：返回 1 = 按下/闭合（动作态），0 = 松开/断开 */
typedef uint8_t (*io_is_pressed_func)(void);

typedef struct KeyScanner {
    io_is_pressed_func is_pressed;   /* 原始状态读取（1 = 按下；永不为空，空指针由 init 换成空实现） */
    uint8_t           stable;       /* 去抖后的稳定状态：1 = 按下 */
    uint8_t           cnt;          /* 与稳定状态不同的连续采样次数 */
    volatile uint8_t  evtPress;     /* 按下沿事件（读取后清除） */
    volatile uint8_t  evtRelease;   /* 松开沿事件（读取后清除） */
    uint16_t          holdCnt;      /* 稳定按下的拍数（饱和，松开清零） */
    uint8_t           inUse;        /* 槽位已分配 */
    uint8_t           scanning;     /* 参与扫描（start 置 1、stop 置 0） */
} KeyScanner;

/* 从静态池分配一个按键句柄：
 *   is_pressed: 原始状态读取回调，传 0 表示“永远不按下”的空实现（便于占位/可选按键）。
 * 去抖时间不按句柄给，统一取项目配置里的 KEY_SCANNER_DEBOUNCE_MS（毫秒，库内折算成拍）。
 * 返回 0 表示池已用尽（KEY_SCANNER_NUM 不够，按键个数是确定的，直接把宏改成实际按键数）。
 * 句柄分配后常驻（池是编译期定死的静态数组），不提供释放接口。
 * 新句柄处于“未参与扫描”状态，需再调用 start。 */
KeyScanner* keyScanner_init(io_is_pressed_func is_pressed);

/* 纳入扫描：立即采样一次作为初始稳定状态（上电即按住的键不会产生假事件），
 * 之后由 keyScanner_scan() 每拍推进去抖与事件生成。 */
void keyScanner_start(KeyScanner* handle);

/* 退出扫描：状态冻结在最后一次采样结果，事件不再产生（切换界面时丢弃积压事件很有用）。 */
void keyScanner_stop(KeyScanner* handle);

/* 节拍函数：由调用方按固定周期调用，遍历所有已 start 的句柄完成去抖与事件生成。 */
void keyScanner_scan(void);

/* 去抖后的稳定状态：1 = 按下 / 0 = 松开（未分配或未 start 的句柄返回 0）。 */
uint8_t keyScanner_isPressed(KeyScanner* handle);
uint8_t keyScanner_isReleased(KeyScanner* handle);

/* 边沿事件：本次扫描以来发生过“松开→按下”返回 1，读取后自动清除。
 * 自复位按键用它做“按一下触发一次”。 */
uint8_t keyScanner_getPressedEvent(KeyScanner* handle);
uint8_t keyScanner_getReleasedEvent(KeyScanner* handle);

/* 丢弃该句柄积压的全部边沿事件。 */
void keyScanner_clearEvents(KeyScanner* handle);

/* 稳定按住的时长（毫秒，按 KEY_SCANNER_CYCLE_MS 换算，饱和到 65535）：松开时为 0。 */
uint16_t keyScanner_getHoldMs(KeyScanner* handle);

/* 长按判定：当前处于稳定按下、且按住时长已达 holdMs 时返回 1（查询值，不自动清除）。 */
uint8_t keyScanner_isLongPressed(KeyScanner* handle, uint16_t holdMs);

#endif /* KEY_SCANNER_a61d2c4e_8f37_4a9b_b0d2_5c7e9f1083ab */
