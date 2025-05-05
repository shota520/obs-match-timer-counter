import obspython as obs
import time

# タイマー関連
start_time = time.time()
paused = False
paused_at = 0

# カウント関連
wins = 0
losses = 0
source_name = ""

# === OBS UI定義 ===
def script_description():
    return "タイマー＋勝敗カウント＋勝率＋合計試合 統合表示スクリプト"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "source_name", "テキストソース名", obs.OBS_TEXT_DEFAULT)

    obs.obs_properties_add_bool(props, "paused", "一時停止")
    obs.obs_properties_add_button(props, "reset_timer", "タイマーリセット", on_reset_timer)

    obs.obs_properties_add_button(props, "add_win", "勝ち＋1", on_add_win)
    obs.obs_properties_add_button(props, "sub_win", "勝ち−1", on_sub_win)
    obs.obs_properties_add_button(props, "add_loss", "負け＋1", on_add_loss)
    obs.obs_properties_add_button(props, "sub_loss", "負け−1", on_sub_loss)

    obs.obs_properties_add_button(props, "reset_counts", "勝敗リセット", on_reset_counts)

    return props

# === スクリプト更新時 ===
def script_update(settings):
    global source_name, paused, paused_at, start_time
    source_name = obs.obs_data_get_string(settings, "source_name")
    was_paused = paused
    paused = obs.obs_data_get_bool(settings, "paused")
    if not was_paused and paused:
        paused_at = time.time()
    elif was_paused and not paused:
        delta = time.time() - paused_at
        start_time += delta

# === タイマー制御 ===
def on_reset_timer(props, prop):
    global start_time
    start_time = time.time()
    return True

# === 勝敗ボタン ===
def on_add_win(props, prop):
    global wins
    wins += 1
    return True

def on_sub_win(props, prop):
    global wins
    wins = max(0, wins - 1)
    return True

def on_add_loss(props, prop):
    global losses
    losses += 1
    return True

def on_sub_loss(props, prop):
    global losses
    losses = max(0, losses - 1)
    return True

def on_reset_counts(props, prop):
    global wins, losses
    wins = 0
    losses = 0
    return True

# === 毎秒実行 ===
def script_tick(seconds):
    global start_time, source_name, paused, wins, losses

    if paused:
        return

    elapsed = int(time.time() - start_time)
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    secs = elapsed % 60
    time_text = f"{hours}:{minutes:02}:{secs:02}"

    total = wins + losses
    winrate = (wins / total * 100) if total > 0 else 0
    summary = (
        f"⏱ {time_text}\n"
        f"勝: {wins}　負: {losses}\n"
        f"合計: {total}　勝率: {winrate:.1f}%"
    )

    source = obs.obs_get_source_by_name(source_name)
    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", summary)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
