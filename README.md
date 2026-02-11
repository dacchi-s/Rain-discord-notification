# Rain Discord Notification Bot

日本の気象庁データを使用した雨雲レーダー Discord 通知 Bot。

Open-Meteo JMA API を利用して指定地点の降水予報を取得し、雨が降りそうな時に Discord へ通知します。

---

A rain cloud radar Discord notification bot using Japan Meteorological Agency data.

Fetches precipitation forecasts for a specified location using Open-Meteo JMA API and sends a Discord notification when rain is expected.

## Features / 機能

- 🌧️ Uses JMA (Japan Meteorological Agency) data / JMAデータを使用
- 📍 Configurable location by latitude/longitude / 緯度経度で地点を設定可能
- ⏱️ Customizable forecast time range (1-96 hours) / 予報時間範囲を設定可能（1〜96時間）
- 🎚️ Adjustable precipitation threshold / 降水しきい値を調整可能
- 📱 Discord webhook notifications / Discord Webhookで通知
- 🔧 Lightweight dependencies (no discord.py required) / 軽量な依存関係（discord.py不要）

## Requirements / 必要な環境

- Python 3.10+
- Discord Webhook URL

## Installation / インストール

```bash
# Clone or download this repository
cd Rain-discord-notification

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration / 設定

### Using .env File / .envファイルを使用（推奨）

```bash
cp .env.example .env
# Edit .env with your settings
vim .env
```

The `.env` file is automatically loaded when the script runs.

スクリプト実行時に `.env` ファイルは自動的に読み込まれます。

### Configuration Options / 設定項目

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | Required |
| `RAIN_LATITUDE` | Latitude / 緯度 | 35.6895 (Shinjuku) |
| `RAIN_LONGITUDE` | Longitude / 経度 | 139.6917 (Shinjuku) |
| `RAIN_THRESHOLD` | Precipitation threshold (mm) / 降水しきい値 | 0.5 |
| `RAIN_HOURS_TO_CHECK` | Hours to check ahead / チェックする時間範囲 | 2 |

## Usage / 使用方法

### Manual Execution / 手動実行

```bash
# Make sure virtual environment is activated
python rain_notifier.py
```

### Scheduled Execution / 定期実行

#### Linux (cron)

```bash
# Edit crontab
crontab -e

# Add line to run every 15 minutes
*/15 * * * * cd /path/to/Rain-discord-notification && source venv/bin/activate && python rain_notifier.py
```

## Discord Notification Format / Discord通知形式

When rain is expected, the following embed message is sent:

雨が予想される場合、以下のEmbedメッセージが送信されます：

```
┌─────────────────────────────────────────────────┐
│ 🌧️ 雨が降りそうです                              │
│ まもなく雨が予想されます。                        │
│                                                 │
│ 予報                                            │
│ `15:00` - 雨 (降水量: 2.5mm)                     │
│ `16:00` - 雨 (降水量: 3.0mm)                     │
│                                                 │
│ 場所                                            │
│ 緯度: 35.6895, 経度: 139.6917                    │
│ (東京都新宿区付近)                               │
│                                                 │
│ Powered by Open-Meteo JMA API                   │
└─────────────────────────────────────────────────┘
```

## API Specifications / API仕様

This bot uses [Open-Meteo JMA API](https://open-meteo.com/en/docs/jma-api).

| Specification | Value |
|---------------|-------|
| **Spatial Resolution** | ~5km (MSM model) |
| **Forecast Length** | Up to 96 hours (4 days) |
| **Time Interval** | Hourly |
| **Update Frequency** | Every 3 hours |

## Example Output / 出力例

```
[2026-02-07 16:44:51] Checking precipitation forecast...
⚠️  Rain expected: 2 occurrence(s)
  - 16:00: 0.7mm (小雨)
  - 17:00: 0.6mm (小雨)
✅ Discord notification sent successfully
```

## License / ライセンス

MIT License

## Data Sources / データソース

- [Open-Meteo](https://open-meteo.com/) - Free Weather API
- [Japan Meteorological Agency](https://www.jma.go.jp/jma/indexe.html)
