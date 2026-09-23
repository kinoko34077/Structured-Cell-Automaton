# Structured-Cell-Automaton Project Overlay

このファイルは既存 `Structured-Cell-Automaton` に追加したKiNoTch Project Overlayの入口です。Streamlit GUIとDomain実装はrootに残します。

## 概要

このRepositoryは、構文セルの生成・抽出・進化・可視化を試すStreamlit GUIプロトタイプです。

- 個別情報・仕様・実装: project/
- 個別プロジェクト定義: project/project.json
- 個別仕様索引: project/docs/INDEX.md
- 現在状態: project/docs/CURRENT_STATE.md
- 共通操作: .kinotch/README_BASE.md

## 所有境界

- Streamlit UI、構文セルDomain、可視化、保存データ、依存管理はProject側の既存実装を正本とします。
- KiNoTch Baseはrepository構造、診断、verify入口を提供します。
- Web Surfaceは既存Streamlit実装を `OVERRIDE` として記録します。

## 最短利用方法

```powershell
.\knt.cmd doctor
.\knt.cmd setup
.\knt.cmd dev
```

既存の研究用説明と機能一覧はroot READMEを参照してください。
