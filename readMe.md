# keyScanner —— 通用按键扫描库

把「去抖 + 稳定状态 + 边沿事件 + 按住时长」做成一个与硬件无关的小库，用法与同目录旁的 `flashCtrl` 一致：
**按键自己在你的项目里接线、自己写读取回调，库只负责按拍扫描和提供查询接口**。

- 每个按键一个句柄，句柄从库内静态内存池分配（数量由 `KEY_SCANNER_NUM` 决定），不用动态内存、不用 `malloc`；
- 库不自己计时，由你按固定周期调用 `keyScanner_scan()`，这个周期就是「一拍」；
- 只依赖 `<stdint.h>`，不依赖任何芯片头文件，因此可以原样搬到别的项目。

## 接入三步

1）项目里新建 `userKeyScannerCfg.h`（照抄 `cfg/userKeyScannerCfg.h.sample`），定义 `KEY_SCANNER_NUM` 和 `KEY_SCANNER_CYCLE_MS`；
2）给每个按键写一个 `is_pressed` 回调，返回 1 表示「按下/闭合」；
3）初始化时 `keyScanner_init` + `keyScanner_start`，之后每拍调用一次 `keyScanner_scan()`。

```c
/* 低电平有效的按键：引脚读到 0 才算按下 */
static uint8_t key1_is_pressed(void) { return (0 == P20) ? 1 : 0; }

KeyScanner* key1;

void app_init(void) {
    key1 = keyScanner_init(key1_is_pressed);   /* 池满时返回 0，句柄不要当状态用 */
    keyScanner_start(key1);                    /* 立即采样一次，上电即按住的键不会产生假事件 */
}

void app_10ms(void) {                       /* 每 10ms 一次，与 KEY_SCANNER_CYCLE_MS 对应 */
    keyScanner_scan();
}

void app_loop(void) {
    if (keyScanner_getPressedEvent(key1)) {    /* 按下沿，读后自动清除 */
        /* 按一下触发一次 */
    }
    if (keyScanner_isPressed(key1) && keyScanner_getHoldMs(key1) >= 1000) {
        /* 长按 1 秒以上 */
    }
}
```

## 接口表

| 接口 | 说明 |
| --- | --- |
| `keyScanner_init(is_pressed)` | 从池中分配一个句柄。`is_pressed` 传 0 时用「永远不按下」的空实现（可做可选按键占位）；池满返回 0 |
| `keyScanner_deinit(h)` | 归还槽位（先退出扫描再清状态），返回后句柄不可用 |
| `keyScanner_start(h)` | 纳入扫描，并立即采样一次作为初始稳定状态 |
| `keyScanner_stop(h)` | 退出扫描，状态冻结、不再产生事件（切换界面时清掉积压事件很有用） |
| `keyScanner_scan()` | 节拍函数，遍历所有已 start 的句柄推进去抖与事件生成 |
| `keyScanner_isPressed(h)` / `keyScanner_isReleased(h)` | 去抖后的稳定状态，1 = 按下 / 0 = 松开 |
| `keyScanner_getPressedEvent(h)` | 松开→按下 边沿，读后自动清除 |
| `keyScanner_getReleasedEvent(h)` | 按下→松开 边沿，读后自动清除 |
| `keyScanner_clearEvents(h)` | 丢弃该句柄积压的边沿事件 |
| `keyScanner_getHoldMs(h)` | 稳定按住的毫秒数（按 `KEY_SCANNER_CYCLE_MS` 换算，饱和 65535），松开为 0 |
| `keyScanner_isLongPressed(h, ms)` | 当前稳定按下且按住已达 `ms` 毫秒 |
| `keyScanner_getUsedCount()` / `keyScanner_getCapacity()` | 已分配数量 / 池容量（定形后据此收紧 `KEY_SCANNER_NUM`） |

## 语义与边界

- **`is_pressed` 的口径与 `flashCtrl` 的 `is_on` 一致：1 = 动作态（按下/闭合）**。低电平有效的按键写成 `return (0 == P20) ? 1 : 0;`，别直接返回引脚电平。
- **对外的时长只认毫秒**：`KEY_SCANNER_DEBOUNCE_MS`、`getHoldMs`、`isLongPressed(h, ms)` 全是毫秒口径，库内自己按 `KEY_SCANNER_CYCLE_MS` 折算成拍。所以不存在「去抖 2 拍」这种说法，也不会把扫描节拍和自己的应用节拍搞混。`KEY_SCANNER_CYCLE_MS` 只是给库做换算用的集成参数，必须等于你调 `keyScanner_scan()` 的真实周期。
- **去抖时间是全局一套**：`KEY_SCANNER_DEBOUNCE_MS` 在 `userKeyScannerCfg.h` 里配一次，所有按键共用，`keyScanner_init` 只收一个读取回调。同板上的键都是同型号、同理的机械抖动，一套值够用；真遇到某个键需要不同去抖，再考虑按句柄加参数（现在故意不做，免得每个注册点都要传一个用不到的参数）。
- **去抖时间的取整**：毫秒向上取整成拍，20ms / 5ms = 4 拍；给 15ms 实际按 3 拍（15ms）执行。想更灵敏就调小（小于一拍仍按 1 拍，等于不去抖），想更稳就调大。
- **事件是粘滞标志，不排队**：同一个键在两次读取之间翻转多次，只留下最后一次事件的痕迹。按键场景够用，也省 RAM；需要逐次不丢就自己加计数。
- **读清竞态**：「读事件 → 清事件」之间若正好被扫描打断置位，这一次事件会丢。扫描在中断里跑、事件在主循环里读时，需要严格不丢就在读清外面包一段 `EA=0 / EA=1`，或改用计数方式。
- **扫描放在哪里**：定时器中断里最理想（节拍稳定，不受主循环长任务影响）。放在主循环里也能用，代价是长任务期间按键响应变慢、按住时长精度下降。
- **`start` 立即采样一次**，所以上电时就按住的键不会立刻产生一次按下事件；`stop` 之后该键的 `isPressed` 保持最后状态，直到再次 `start`。
- **句柄字段由库内维护**：`inUse`、`scanning` 被外部改动会破坏分配与扫描逻辑，`is_pressed`/`stable` 等也不要在外部写。
- **没有链表**：句柄在池里的位置固定，扫描就是按槽位顺序遍历，所以 `start` / `stop` 只是写一个单字节，不像 `flashCtrl` 那样需要「请求—节拍内执行」的队列。
- **`KEY_SCANNER_NUM` 就是 RAM**：池大小 = `KEY_SCANNER_NUM * sizeof(KeyScanner)`，按实际按键数量给。
