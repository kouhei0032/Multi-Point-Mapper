# Multi-Point-Mapper

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=Leaflet&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-%237EBC6F.svg?style=for-the-badge&logo=OpenStreetMap&logoColor=white)

![GSI API](https://img.shields.io/badge/Data-GSI_Japan-green?style=for-the-badge)
![OSRM](https://img.shields.io/badge/Routing-OSRM-lightgrey?style=for-the-badge)

お客様名と住所を入力することで、複数地点を地図にマッピングするシステムです。
経路の算出をすることも可能です。

## アプリリンク（App Link）
このアプリは以下のURLから利用できます。

[![Open in Streamlit](https://img.shields.io/badge/Open%20in%20Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://multi-point-mapper.streamlit.app/)

## 背景　(Background)
営業現場や配送業務において、複数の訪問先を効率的に回るためのルート構築は個人の経験に頼る部分が多く、
大きな工数がかかるかと思います。

本プロジェクトは以下の課題を解決するために開発したプロジェクトです。
* 大量の住所データを手動でプロットする手間の解消
* 効率的な訪問ルートの可視化による業務の効率化
* チーム内での利用状況の可視化

## 特徴 (Features）

* **一括マッピング**: 複数のお客様所在地を地図上に可視化。
* **経路最適化**: マッピングした住所間の効率的な訪問経路を算出。
* **インタラクティブ操作**: Streamlitによる直感的なUIで、地図の操作が可能。
* **管理者アカウント**: 管理者アカウントでどのようなIDが利用しているか可視化できる。

## デモ (Demo)

<img width="646" height="334" alt="image" src="https://github.com/user-attachments/assets/c2878b6c-772b-41c4-8cd3-9cd7ef0b7b61" />
<img width="628" height="595" alt="screenshot_mpm2" src="https://github.com/user-attachments/assets/52b65127-76d2-4ab3-b0bb-54d576a972d4" />
<img width="1211" height="647" alt="image" src="https://github.com/user-attachments/assets/e81d9c6f-8795-4fb4-991d-9dc9b9fa2a95" />


## 動作要件 (Prerequisites)
* Python3.13

## インストール (Installation)
必要なライブラリのインストール
```bash
   pip install streamlit folium streamlit-folium
```

⚠️ ご利用にあたっての注意点
本アプリはルート検索にOSRMのデモサーバー、ジオコーディングに国土地理院APIを使用しています。これらは共有のインフラであるため、
一度に数百件を超えるような大量のデータ投入や、連続したリクエストは控えてください。
