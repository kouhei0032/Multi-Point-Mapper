# プロジェクト名 (Multi-Point-Mapper）

お客様名と住所を入力することで、複数地点を地図にマッピングするシステムです。
経路の算出をすることも可能です。

## 特徴 (Features）

* **一括マッピング**: 複数のお客様所在地を地図上に可視化。
* **経路最適化**: マッピングした住所間の効率的な訪問経路を算出。
* **インタラクティブ操作**: Streamlitによる直感的なUIで、地図の操作が可能。
* **管理者アカウント**: 管理者アカウントでどのようなIDが利用しているか可視化できる。

## デモ (Demo)

<img width="646" height="334" alt="image" src="https://github.com/user-attachments/assets/c2878b6c-772b-41c4-8cd3-9cd7ef0b7b61" />
<img width="421" height="256" alt="screenshot_mpm2" src="https://github.com/user-attachments/assets/04fb19dd-bc1d-43df-aee2-c78bfe35aa61" />



## セットアップ (Setup)

プロジェクトをローカル環境で動かすための手順です。

### 動作要件 (Prerequisites)

* Python3.13

### インストール (Installation)
必要なライブラリのインストール
```bash
   pip install streamlit folium streamlit-folium
