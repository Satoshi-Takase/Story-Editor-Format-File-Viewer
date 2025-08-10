# SEF Reader - Story Editor Format File Viewer

SEFリーダー - Story Editor形式ファイルビューア

Professional SEF (Story Editor Format) Novel File Reader Application  
プロフェッショナル SEF（Story Editor形式）小説ファイルリーダーアプリケーション

## 📖 Overview / 概要

This application is a dedicated reader for `.SEF` format novel files created with Story Editor. It provides a beautiful tree-structured display of chapter hierarchies and presents content in a highly readable format.

このアプリケーションは、Story Editorで作成された`.SEF`形式の小説ファイル専用リーダーです。美しいツリー構造で章立てを表示し、内容を読みやすい形式で表示します。

### ✨ Key Features / 主な機能

- **🌳 Tree Structure Display / ツリー構造表示**: Intuitive hierarchical display of novel chapter structure / 小説の章構造を直感的な階層表示
- **📖 Dual-Pane Interface / デュアルペインインターフェース**: Chapter list on the left, content display on the right / 左側に章リスト、右側に内容表示
- **🔍 Perfect Structure Analysis / 完璧な構造解析**: Accurate parsing of internal SEF file structure / SEFファイル内部構造の正確な解析
- **💾 Multi-Format Support / マルチフォーマット対応**: Compatible with various SEF file formats / 様々なSEFファイル形式に対応
- **🎯 1:1 Complete Mapping / 1:1完全対応**: Perfect correspondence between hierarchy and content / 階層と内容の完璧な対応関係

## 🚀 Usage / 使用方法

### 1. Launch the Application / アプリケーションの起動

```bash
python gui_sef_reader.py
```

### 2. Open SEF File / SEFファイルを開く

- Click "📁 Open SEF File / SEFファイルを開く" button / 「📁 Open SEF File / SEFファイルを開く」ボタンをクリック
- Select your `.SEF` file / `.SEF`ファイルを選択

### 3. Read Your Novel / 小説を読む

- Select chapters from the tree structure on the left / 左側のツリー構造から章を選択
- Content automatically displays on the right / 右側に内容が自動表示
- Tree structure supports expand/collapse functionality / ツリー構造は展開/折りたたみ機能をサポート

## 📁 File Structure / ファイル構成

- `gui_sef_reader.py` - Main application / メインアプリケーション
- `SEF-Format-Specification.md` - Technical specification (English & Japanese) / 技術仕様書（英語・日本語）
- `README.md` - This file / このファイル

## 🔧 Technical Specifications / 技術仕様

- **Supported Format / 対応形式**: Story Editor Format (.SEF)
- **Internal Structure / 内部構造**: 3-layer architecture (Header + ZLIB Compressed Data + Hierarchy Information) / 3層アーキテクチャ（ヘッダー + ZLIB圧縮データ + 階層情報）
- **Character Encoding / 文字エンコード**: Shift-JIS with multi-encoding fallback support / マルチエンコードフォールバック対応のShift-JIS
- **GUI Framework**: tkinter (Python Standard Library) / Python標準ライブラリ
- **Requirements / 要件**: Python 3.6+

## 📖 Technical Documentation / 技術文書

For detailed technical information about the SEF format:

SEFフォーマットに関する詳細な技術情報については：

- **English & Japanese / 英語・日本語**: See `SEF-Format-Specification.md`

This document includes:

この文書には以下が含まれています：

- Complete file structure analysis / 完全なファイル構造解析
- Parsing algorithms / 解析アルゴリズム
- Implementation guidelines / 実装ガイドライン
- Known issues and solutions / 既知の問題と解決策

## 💡 Development History / 開発履歴

This project was developed through collaborative efforts, overcoming various technical challenges:

このプロジェクトは、様々な技術的課題を克服しながら、協力的な開発によって完成しました：

1. **SEF Structure Analysis / SEF構造解析**: Detailed binary format analysis / 詳細なバイナリフォーマット解析
2. **ZLIB Decompression / ZLIB展開**: Accurate compressed data restoration / 正確な圧縮データ復元
3. **Hierarchy Structure Parsing / 階層構造解析**: Chapter organization extraction from plain text sections / プレーンテキスト部分からの章構成抽出
4. **RTF-to-Text Conversion / RTF-テキスト変換**: Complex Rich Text Format to plain text processing / 複雑なリッチテキスト形式のプレーンテキスト処理
5. **1:1 Mapping Implementation / 1:1マッピング実装**: Perfect correspondence between hierarchy and content / 階層と内容の完璧な対応関係
6. **Tree Display Realization / ツリー表示実現**: Evolution from flat list to true hierarchical display / フラットリストから真の階層表示への進化

## 📋 Installation Requirements / インストール要件

### Prerequisites / 前提条件

- Python 3.6 or higher / Python 3.6以上
- Standard Python libraries (tkinter, zlib, struct, re) / Python標準ライブラリ (tkinter, zlib, struct, re)

### Installation / インストール

1. Clone or download this repository / このリポジトリをクローンまたはダウンロード
2. Ensure Python 3.6+ is installed / Python 3.6+がインストールされていることを確認
3. Run the application / アプリケーションを実行:

   ```bash
   python gui_sef_reader.py
   ```

## 🚀 Creating Executable Files / 実行ファイルの作成

For easier launching, you can create executable files for your platform:

より簡単に起動するために、お使いのプラットフォーム用の実行ファイルを作成できます：

### Windows (.bat file) / Windows（.batファイル）

Create a file named `launch.bat` / `launch.bat` という名前のファイルを作成：

```batch
@echo off
chcp 65001
echo Starting SEF Reader...
python gui_sef_reader.py
pause
```

### macOS/Linux (.sh file) / macOS/Linux（.shファイル）

Create a file named `launch.sh` / `launch.sh` という名前のファイルを作成：

```bash
#!/bin/bash
echo "Starting SEF Reader..."
python3 gui_sef_reader.py
```

Make it executable / 実行可能にする：

```bash
chmod +x launch.sh
```

### Python Launcher (Cross-platform) / Pythonランチャー（クロスプラットフォーム）

Create a file named `launch.py` / `launch.py` という名前のファイルを作成：

```python
#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    print("Starting SEF Reader...")
    try:
        # Try to run the main application
        subprocess.run([sys.executable, "gui_sef_reader.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
    except FileNotFoundError:
        print("Error: gui_sef_reader.py not found!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
```

## 🛠️ Features in Detail / 機能詳細

### Advanced Parsing Engine / 高度な解析エンジン

- **Binary Header Analysis / バイナリヘッダー解析**: Accurate interpretation of 16-byte SEF headers / 16バイトSEFヘッダーの正確な解釈
- **ZLIB Decompression / ZLIB展開**: Robust decompression with error handling / エラーハンドリング付きの堅牢な展開
- **Multi-Encoding Support / マルチエンコード対応**: Shift-JIS with automatic fallback detection / 自動フォールバック検出付きShift-JIS
- **RTF Processing / RTF処理**: Complete Rich Text Format parsing and conversion / 完全なリッチテキスト形式の解析と変換

### User Interface / ユーザーインターフェース

- **Responsive Design / レスポンシブデザイン**: Scales to different screen sizes / 異なる画面サイズに対応
- **Intuitive Navigation / 直感的なナビゲーション**: Tree-based chapter selection / ツリーベースの章選択
- **Content Display / コンテンツ表示**: Formatted text display with metadata / メタデータ付きの整形テキスト表示
- **Status Feedback / ステータスフィードバック**: Real-time processing status and file information / リアルタイム処理状況とファイル情報

### Performance Optimization / パフォーマンス最適化

- **Asynchronous Loading / 非同期読み込み**: Non-blocking file processing / ノンブロッキングファイル処理
- **Memory Efficient / メモリ効率**: Optimized for large SEF files / 大容量SEFファイル用に最適化
- **Single Instance Control / シングルインスタンス制御**: Prevents multiple application instances / 複数アプリケーションインスタンスを防止

## 🔒 Security Features / セキュリティ機能

- **Input Validation / 入力検証**: Comprehensive file format verification / 包括的なファイル形式検証
- **Error Handling / エラーハンドリング**: Graceful handling of corrupted or invalid files / 破損または無効なファイルの適切な処理
- **Safe Text Processing / 安全なテキスト処理**: Sanitized content display / サニタイズされたコンテンツ表示
- **Memory Protection / メモリ保護**: Prevents resource exhaustion attacks / リソース枯渇攻撃の防止

## 🤝 Contributing / 貢献

This project welcomes contributions. Please ensure:

このプロジェクトでは貢献を歓迎します。以下をお守りください：

1. Follow Python coding standards (PEP 8) / Pythonコーディング標準（PEP 8）に従う
2. Include appropriate documentation / 適切なドキュメントを含める
3. Test with various SEF file formats / 様々なSEFファイル形式でテストする
4. Maintain backward compatibility / 後方互換性を維持する

## 📄 License / ライセンス

This project is open source. Please refer to the license file for usage terms.

このプロジェクトはオープンソースです。使用条件についてはライセンスファイルをご参照ください。

## 🙏 Acknowledgments / 謝辞

This application was developed with advanced AI assistance, utilizing state-of-the-art language models for problem-solving and code generation.

このアプリケーションは、問題解決とコード生成に最先端の言語モデルを活用した、高度なAI支援により開発されました。

---
**Technical Achievement / 技術的成果**: Complete reverse engineering and implementation of SEF format support with professional-grade parsing and display capabilities. / プロフェッショナルグレードの解析・表示機能を備えたSEFフォーマットサポートの完全リバースエンジニアリングと実装。
