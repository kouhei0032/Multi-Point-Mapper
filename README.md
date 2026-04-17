# プロジェクト名 (Multi-Point-Mapper）

お客様名と住所を入力することで、複数地点を地図にマッピングするシステムです。
経路の算出をすることも可能になっています。

## 特徴 (Features）

* **一括マッピング**: 複数のお客様所在地を地図上に可視化。
* **経路最適化**: マッピングした住所間の効率的な訪問経路を算出。
* **インタラクティブ操作**: Streamlitによる直感的なUIで、地図の操作が可能。
* **管理者アカウント**: 管理者アカウントでログインすることでどのようなIDが利用しているか可視化することが可能。

## デモ (Demo)

<img width="649" height="320" alt="image" src="https://github.com/user-attachments/assets/65a52f34-a8bb-4dd9-953a-610ad3a6f48c" />

## セットアップ (Setup)

プロジェクトをローカル環境で動かすための手順です。

### 動作要件 (Prerequisites)

* Python3.13

### インストール (Installation)
必要なライブラリのインストール
```bash
   pip install streamlit folium streamlit-folium
