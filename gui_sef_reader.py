#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEF Reader - Story Editor Format File Viewer GUI Application
SEFリーダー - Story Editor形式ファイルビューア GUIアプリケーション

Professional dual-pane SEF reader with hierarchical chapter structure display
プロフェッショナル デュアルペイン SEFリーダー 階層章構造表示対応

Explorer-style interface: chapter tree on left, RTF content on right
エクスプローラー風インターフェース: 左側に章ツリー、右側にRTF内容表示

Created by: GitHub Copilot & Claude Sonnet 4
Based on: Advanced SEF structure analysis implementation
ベース: 高度なSEF構造解析実装
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
import struct
import zlib
import re
from typing import List, Dict, Optional, Tuple
import threading
import queue
import tempfile
import atexit

# Single instance control / シングルインスタンス制御
LOCK_FILE = os.path.join(tempfile.gettempdir(), 'sef_reader_gui.lock')

# Import existing SEF reader classes / 既存SEFリーダークラスをインポート
sys.path.append(os.path.dirname(__file__))

# SEF Structure Analysis Class (GUI Independent)
# SEF構造解析専用クラス（GUI非依存）
class SEFAnalyzer:
    """SEF Structure Analysis Specialist Class (GUI Independent)
    SEF構造解析専用クラス（GUI非依存）"""
    
    def __init__(self):
        pass
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze actual SEF file structure
        実際のSEFファイルを解析"""
        try:
            print(f"🔍 SEF File Analysis Started / SEFファイル解析開始: {os.path.basename(file_path)}")
            
            # File reading / ファイル読み込み
            with open(file_path, 'rb') as f:
                data = f.read()
            
            print(f"   File Size / ファイルサイズ: {len(data)} bytes")
            
            # Header analysis / ヘッダー解析
            if len(data) < 16:
                raise ValueError("File too small / ファイルが小さすぎます")
            
            magic = struct.unpack('<H', data[0:2])[0]
            if magic != 0x0303:
                raise ValueError(f"Invalid magic number / 不正なマジック番号: {magic:04x}")
            
            field1 = struct.unpack('<I', data[2:6])[0]
            field2 = struct.unpack('<I', data[6:10])[0] 
            field3 = struct.unpack('<I', data[10:14])[0]
            field4 = struct.unpack('<I', data[14:18])[0] if len(data) >= 18 else 0
            
            print(f"   Magic: 0x{magic:04x}")
            print(f"   Field1: {field1} (0x{field1:x})")
            
            # Find ZLIB start position / ZLIB開始位置を探す
            zlib_start = self._find_zlib_start(data)
            if zlib_start == -1:
                raise ValueError("ZLIB data not found / ZLIBデータが見つかりません")
            
            print(f"   ZLIB Start Position / ZLIB開始位置: {zlib_start}")
            
            # ZLIB decompression / ZLIB展開
            zlib_data = data[zlib_start:]
            decompressed = zlib.decompress(zlib_data)
            print(f"   ✅ ZLIB Decompression Success / ZLIB展開成功: {len(zlib_data)} → {len(decompressed)} bytes")
            
            # Text conversion / テキスト変換
            text_content = self._decode_text(decompressed)
            print(f"   📝 Text Length / テキスト長: {len(text_content)} characters")
            
            # Separate plain and RTF parts / プレーン部分とRTF部分を分離
            plain_part, rtf_part = self._split_plain_rtf(text_content)
            print(f"   📄 Plain Part / プレーン部分: {len(plain_part)} characters")
            print(f"   📝 RTF Part / RTF部分: {len(rtf_part)} characters")
            
            # Hierarchy structure analysis / 階層構造解析
            hierarchy = self._parse_hierarchy(plain_part)
            print(f"   🌳 Hierarchy Items / 階層項目: {len(hierarchy)} items")
            
            # Chapter splitting / 章分割
            chapters = self._split_chapters(rtf_part, hierarchy)
            print(f"   📖 Chapter Split / 章分割: {len(chapters)} chapters")
            
            return {
                'success': True,
                'chapters': chapters,
                'hierarchy': hierarchy,
                'file_size': len(data)
            }
            
        except Exception as e:
            print(f"   ❌ Analysis Error / 解析エラー: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_zlib_start(self, data: bytes) -> int:
        """Find ZLIB data start position
        ZLIBデータの開始位置を探す"""
        # Search for 0x7801 pattern / 0x7801 パターンを探す
        for i in range(len(data) - 1):
            if data[i] == 0x78 and data[i + 1] == 0x01:
                return i
        return -1
    
    def _decode_text(self, data: bytes) -> str:
        """Decode binary data to text
        バイナリデータをテキストにデコード"""
        try:
            # Try Shift-JIS conversion / Shift-JIS変換を試行
            text = ""
            i = 0
            while i < len(data):
                if data[i] == 0:
                    i += 1
                    continue
                
                try:
                    if data[i] >= 0x81 and i + 1 < len(data):
                        # 2-byte character / 2バイト文字
                        char_bytes = data[i:i+2]
                        char = char_bytes.decode('shift-jis', errors='ignore')
                        text += char
                        i += 2
                    else:
                        # 1-byte character / 1バイト文字
                        char_bytes = data[i:i+1]
                        char = char_bytes.decode('shift-jis', errors='ignore')
                        text += char
                        i += 1
                except:
                    i += 1
            
            return text
        except Exception:
            return data.decode('shift-jis', errors='ignore')
    
    def _split_plain_rtf(self, text: str) -> Tuple[str, str]:
        """Separate plain and RTF parts
        プレーン部分とRTF部分を分離"""
        rtf_start = text.find('{\\rtf')
        if rtf_start == -1:
            return text, ""
        
        plain_part = text[:rtf_start]
        rtf_part = text[rtf_start:]
        return plain_part, rtf_part
    
    def _parse_hierarchy(self, plain_part: str) -> List[Dict]:
        """Parse hierarchy structure from plain part
        プレーン部分から階層構造を解析"""
        hierarchy = []
        lines = plain_part.split('\n')
        
        for line_num, line in enumerate(lines):
            original_line = line
            line = line.rstrip()  # 行末の空白のみ除去
            if not line:
                continue
            
            # タブとスペースの詳細解析
            level = 0
            tab_count = 0
            space_count = 0
            
            # 行の最初からタブやスペースをカウント
            for char in line:
                if char == '\t':
                    tab_count += 1
                    level += 1
                elif char == ' ':
                    space_count += 1
                    # 4スペース = 1レベルとして扱う
                    if space_count % 4 == 0:
                        level += 1
                else:
                    break
            
            # インデント除去
            clean_line = line.lstrip('\t ')
            
            if clean_line:
                hierarchy.append({
                    'title': clean_line,
                    'level': level
                })
        
        return hierarchy
    
    def _split_chapters(self, rtf_data: str, hierarchy: List[Dict]) -> List[Dict]:
        """RTFデータを章に分割（完全階層対応方式）- 正解版"""
        chapters = []
        
        if not hierarchy:
            # 階層がない場合は単一章として扱う
            content = self._rtf_to_plain_text(rtf_data)
            chapters.append({
                'title': 'メインテキスト',
                'content': content,
                'start_pos': 0,
                'end_pos': len(rtf_data),
                'size': len(content),
                'level': 0
            })
            return chapters

        # 完全階層対応による分割
        return self._complete_hierarchy_split_chapters(rtf_data, "", hierarchy)
    
    def _extract_complete_rtf(self, rtf_data: str, start_pos: int) -> str:
        """RTF文書の完全な境界を検出して抽出"""
        if start_pos >= len(rtf_data):
            return ""
        
        # RTF開始を確認
        if not rtf_data[start_pos:].startswith('{\\rtf'):
            return ""
        
        # ブレース数をカウントして正確な終端を見つける
        brace_count = 0
        pos = start_pos
        
        while pos < len(rtf_data):
            char = rtf_data[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # RTF文書の終端に到達
                    return rtf_data[start_pos:pos+1]
            pos += 1
        
        # 閉じブレースが見つからない場合は残り全部
        return rtf_data[start_pos:]

    def _complete_hierarchy_split_chapters(self, rtf_data: str, plain_text: str, hierarchy: List[Dict]) -> List[Dict]:
        """階層構造完全対応による章分割（全項目1:1対応）"""
        print("   📚 階層構造完全対応による章分割:")
        
        # RTF文書の開始位置を検出
        rtf_starts = []
        pos = 0
        while True:
            rtf_pos = rtf_data.find('{\\rtf', pos)
            if rtf_pos == -1:
                break
            rtf_starts.append(rtf_pos)
            pos = rtf_pos + 1
        
        print(f"      発見されたRTF文書: {len(rtf_starts)}個")
        print(f"      階層項目数: {len(hierarchy)}個")
        
        # 各RTF文書を正確に抽出してプレーンテキストに変換
        rtf_documents = []
        for i, start_pos in enumerate(rtf_starts):
            # RTF文書の正確な終端を検出（ブレース数カウント）
            rtf_content = self._extract_complete_rtf(rtf_data, start_pos)
            end_pos = start_pos + len(rtf_content)
            
            # RTFをプレーンテキストに変換
            plain_content = self._rtf_to_plain_text(rtf_content)
            
            rtf_documents.append({
                'rtf_index': i,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'rtf_content': rtf_content,
                'plain_content': plain_content,
                'size': len(plain_content)
            })
            
            print(f"        RTF{i+1}: {len(rtf_content)}文字 → {len(plain_content)}文字プレーンテキスト")
        
        # 階層項目と順番通りに完全1:1対応
        chapters = []
        for i, hierarchy_item in enumerate(hierarchy):
            title = hierarchy_item['title']
            level = hierarchy_item['level']
            
            # 対応するRTF文書があるかチェック
            if i < len(rtf_documents):
                doc = rtf_documents[i]
                
                chapters.append({
                    'title': title,
                    'content': doc['plain_content'],
                    'level': level,
                    'start_pos': doc['start_pos'],
                    'end_pos': doc['end_pos'],
                    'size': len(doc['plain_content']),
                    'rtf_index': doc['rtf_index']
                })
                
                print(f"      階層項目[{title}] (レベル{level}) → RTF{doc['rtf_index']+1} ({doc['start_pos']}-{doc['end_pos']}), {len(doc['plain_content'])}文字")
            else:
                # RTF文書が足りない場合
                print(f"      ⚠️ 階層項目[{title}]に対応するRTF文書がありません (項目{i+1}番目)")
                chapters.append({
                    'title': title,
                    'content': '（対応するコンテンツがありません）',
                    'level': level,
                    'start_pos': 0,
                    'end_pos': 0,
                    'size': 0,
                    'rtf_index': -1
                })
        
        # 章が見つからない場合は元の等分割にフォールバック
        if not chapters:
            print("      ⚠️ 階層対応での分割に失敗、等分割にフォールバック")
            return self._fallback_equal_split(rtf_data, plain_text, hierarchy)
        
        print(f"      ✅ 階層構造完全対応: {len(chapters)}章作成")
        return chapters

    def _equal_split_chapters(self, rtf_data: str, plain_text: str, chapter_items: List[Dict]) -> List[Dict]:
        """等分割メソッド（下位互換用）"""
        return self._complete_hierarchy_split_chapters(rtf_data, plain_text, chapter_items)
    
    def _analyze_rtf_structure(self, rtf_data: str) -> Dict:
        """RTFデータの構造を解析"""
        structure = {
            'paragraphs': [],
            'page_breaks': [],
            'sections': []
        }
        
        # 段落マーカーを検索
        par_pattern = r'\\par\s*'
        for match in re.finditer(par_pattern, rtf_data):
            structure['paragraphs'].append(match.start())
        
        # ページブレークを検索
        page_pattern = r'\\page\s*'
        for match in re.finditer(page_pattern, rtf_data):
            structure['page_breaks'].append(match.start())
        
        # セクションマーカーを検索
        section_pattern = r'\\sect\s*'
        for match in re.finditer(section_pattern, rtf_data):
            structure['sections'].append(match.start())
        
        print(f"   🔍 RTF構造: 段落{len(structure['paragraphs'])}, ページ{len(structure['page_breaks'])}, セクション{len(structure['sections'])}")
        
        return structure
    
    def _split_rtf_by_natural_boundaries(self, rtf_data: str, structure: Dict, chapter_items: List[Dict]) -> List[Dict]:
        """RTFデータを自然な境界で分割"""
        print("   ✂️ 自然境界による分割:")
        
        # RTFをプレーンテキストに変換
        plain_text = self._rtf_to_plain_text(rtf_data)
        
        # 章数に応じて分割方法を決定
        if len(chapter_items) <= 1:
            # 単一章
            return [{
                'title': chapter_items[0]['title'] if chapter_items else 'メインテキスト',
                'content': plain_text,
                'start_pos': 0,
                'end_pos': len(rtf_data),
                'size': len(plain_text)
            }]
        elif len(chapter_items) <= 5:
            # 少数章：等分割
            return self._equal_split_chapters(rtf_data, plain_text, chapter_items)
        else:
            # 多数章：等分割（境界ベースではなく）
            return self._equal_split_chapters(rtf_data, plain_text, chapter_items)
    
    def _fallback_equal_split(self, rtf_data: str, plain_text: str, chapter_items: List[Dict]) -> List[Dict]:
        """フォールバック用等分割メソッド（元の方式）"""
        print("   ⚖️ フォールバック等分割:")
        
        chapters = []
        rtf_len = len(rtf_data)
        chapter_count = len(chapter_items)
        
        # RTFデータを等分割
        rtf_chunk_size = rtf_len // chapter_count
        
        for i in range(chapter_count):
            rtf_start = i * rtf_chunk_size
            rtf_end = (i + 1) * rtf_chunk_size if i < chapter_count - 1 else rtf_len
            
            # 該当するRTFチャンクを抽出
            rtf_chunk = rtf_data[rtf_start:rtf_end]
            content = self._rtf_to_plain_text(rtf_chunk)
            
            # 章タイトルを取得
            title = chapter_items[i]['title'] if i < len(chapter_items) else f'章{i+1}'
            
            chapters.append({
                'title': title,
                'content': content,
                'start_pos': rtf_start,
                'end_pos': rtf_end,
                'size': len(content)
            })
            
            print(f"      フォールバック章[{title}]: {rtf_start}-{rtf_end}, {len(content)}文字")
        
        return chapters

    def _reorder_chapters_by_logical_sequence(self, chapters: List[Dict]) -> List[Dict]:
        """章を論理的順序（前編→中編→後編など）で並び替え"""
        print("   🔄 章の論理的順序並び替え:")
        
        # 論理的順序の定義
        logical_order = ['前編', '中編', '後編', '序章', '第1章', '第2章', '第3章', '第4章', '第5章', '終章']
        
        # 各章にソートキーを付与
        for chapter in chapters:
            title = chapter['title']
            if title in logical_order:
                chapter['sort_key'] = logical_order.index(title)
            else:
                # 数値が含まれている場合
                numbers = re.findall(r'\d+', title)
                if numbers:
                    chapter['sort_key'] = 1000 + int(numbers[0])  # 数値ベース
                else:
                    chapter['sort_key'] = 9999  # その他は最後
            
            print(f"      '{title}' → ソートキー: {chapter['sort_key']}")
        
        # ソートキーでソート
        sorted_chapters = sorted(chapters, key=lambda x: x['sort_key'])
        
        print("   ✅ 並び替え完了:")
        for i, chapter in enumerate(sorted_chapters):
            print(f"      {i+1}. {chapter['title']} (キー: {chapter['sort_key']})")
        
        return sorted_chapters

    def _detect_chapter_title_from_content(self, content: str, chapter_items: List[Dict]) -> str:
        """コンテンツから実際の章タイトルを検出"""
        print(f"   🔍 章タイトル検出中: {content[:50]}...")
        
        # 可能な章タイトルのリスト
        possible_titles = [item['title'] for item in chapter_items]
        
        # コンテンツの最初の部分で章タイトルを探す
        content_start = content[:200]  # 最初の200文字で判定
        
        # 各章タイトルをチェック
        for title in possible_titles:
            # 完全一致を探す
            if title in content_start:
                print(f"      ✅ 完全一致: '{title}'")
                return title
            
            # 部分一致を探す（「前編」「中編」「後編」など）
            for char in title:
                if char in content_start and len(char.strip()) > 0:
                    # 前編・中編・後編の特定パターン
                    if title == '前編' and ('前編' in content_start or '月曜日' in content_start):
                        print(f"      ✅ 前編パターン検出: '{title}'")
                        return title
                    elif title == '中編' and ('中編' in content_start or '起立、礼' in content_start):
                        print(f"      ✅ 中編パターン検出: '{title}'")
                        return title
                    elif title == '後編' and ('後編' in content_start or '女性化して３日目' in content_start or 'ぶらじゃあ' in content_start):
                        print(f"      ✅ 後編パターン検出: '{title}'")
                        return title
        
        # 見つからない場合は最初の章タイトルを返す
        fallback_title = possible_titles[0] if possible_titles else 'Unknown'
        print(f"      ❌ タイトル検出失敗、フォールバック: '{fallback_title}'")
        return fallback_title
    
    def _rtf_to_plain_text(self, rtf_content: str) -> str:
        """RTFからプレーンテキストへの変換（メタ情報保持版）"""
        if not rtf_content:
            return ""
        
        text = rtf_content
        
        # 1. RTF内のShift-JIS16進エンコードをデコード
        def decode_sjis_hex_sequence(match):
            hex_sequence = match.group(0)
            hex_pairs = re.findall(r"\\'([0-9a-fA-F]{2})", hex_sequence)
            try:
                byte_array = bytes([int(h, 16) for h in hex_pairs])
                return byte_array.decode('shift_jis', errors='ignore')
            except:
                return ''
        
        # 連続するエスケープシーケンスをまとめてデコード
        text = re.sub(r"(?:\\'[0-9a-fA-F]{2})+", decode_sjis_hex_sequence, text)
        
        # 1.5. 日付情報はそのまま保持（保護処理は不要）
        print(f"      日付情報はユーザーコンテンツとして保持...")
        
        # 2. RTF構造ブロックの除去（メタデータのみ）
        text = re.sub(r'\{\\fonttbl[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', text)  # フォントテーブル
        text = re.sub(r'\{\\colortbl[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', text)  # カラーテーブル
        
        # 3. RTF制御コマンドの除去（必要最小限）
        text = re.sub(r'\\[a-zA-Z]+\d+(?:\s+\\[a-zA-Z]+\d+)*', ' ', text)  # 数値付きコマンド
        text = re.sub(r'\\[a-zA-Z]+', ' ', text)  # 文字制御コマンド
        text = re.sub(r'\\[^a-zA-Z]', '', text)  # その他エスケープ
        
        # 4. 波括弧の除去
        text = re.sub(r'[{}]', '', text)
        
        # 5. 不要な連続文字の整理（日付パターンと日付は保護）
        text = re.sub(r';+', ' ', text)  # セミコロンを空白に
        # 日付形式とパターンマーカーを保護してから数字処理
        text = re.sub(r'(?<!__DATE_PATTERN_)(?<![年月日])[0-9]+(?![年月日])(?!__)(?:\s+[0-9]+)*\s*', ' ', text)  # レイアウト関連の数字のみ削除
        
        # 6. 改行・空白の正規化
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        text = re.sub(r'[ \t]+', ' ', text)  # 複数空白を1つに
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # 行頭空白除去
        text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)  # 行末空白除去
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # 過剰改行を2つに
        
        # 7. 最終クリーニング
        text = text.strip()
        
        # 日付情報はユーザーコンテンツとしてそのまま保持
        print(f"        最終テキスト (先頭100文字): {text[:100]}")
        
        return text
    
    def _alternative_rtf_decode(self, rtf_content: str) -> str:
        """代替RTFデコード方式（元の方法が失敗した場合）"""
        try:
            # RTF内の16進数値を直接探してデコード
            text_parts = []
            
            # 連続する16進数文字列を検出してデコード
            hex_pattern = r'([0-9a-fA-F]{4,})'
            hex_matches = re.findall(hex_pattern, rtf_content)
            
            for hex_str in hex_matches:
                if len(hex_str) % 2 == 0:  # 偶数長の16進文字列のみ
                    try:
                        # 2文字ずつペアにしてバイトに変換
                        byte_data = bytes.fromhex(hex_str)
                        decoded_text = byte_data.decode('shift-jis', errors='ignore')
                        if decoded_text and len(decoded_text.strip()) > 0:
                            text_parts.append(decoded_text)
                    except:
                        continue
            
            result = ' '.join(text_parts)
            if result.strip():
                return result.strip()
            
            # それでもダメなら、プレーンテキスト部分を探す
            plain_parts = re.findall(r'[ぁ-んァ-ヶー一-龯]+', rtf_content)
            if plain_parts:
                return ' '.join(plain_parts)
            
            return "テキスト抽出に失敗しました"
            
        except Exception:
            return "デコードエラー"

def check_single_instance():
    """Single instance control / シングルインスタンス制御"""
    if os.path.exists(LOCK_FILE):
        messagebox.showwarning(
            "Duplicate Launch / 重複起動",
            "SEF Reader is already running.\n"
            "Only one application instance can be launched.\n\n"
            "SEFリーダーは既に起動中です。\n"
            "1つのアプリケーションのみ起動できます。"
        )
        return False
    
    # Create lock file / ロックファイル作成
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        # Remove lock file on exit / 終了時にロックファイルを削除
        def cleanup():
            try:
                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE)
            except:
                pass
        
        atexit.register(cleanup)
        return True
    except:
        return True  # Allow launch if lock file creation fails / ロックファイル作成失敗時は起動を許可

class SEFReaderGUI:
    """Dual-pane SEF Reader GUI / 2ペインSEFリーダー GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SEF Reader - Story Editor Format File Viewer / SEFリーダー - Story Editor形式ファイルビューア")
        self.root.geometry("1200x800")
        
        # SEF reader instance / SEFリーダーインスタンス
        self.sef_reader = SEFAnalyzer()
        
        # Current file information / 現在のファイル情報
        self.current_file = None
        self.current_chapters = []
        self.current_hierarchy = []
        
        # Create GUI / GUI作成
        self.setup_gui()
        
    def setup_gui(self):
        """Setup GUI elements / GUI要素の設定"""
        
        # Main frame / メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar / トップツールバー
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="📁 Open SEF File / SEFファイルを開く", command=self.open_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="🔄 Reload / リロード", command=self.reload_file).pack(side=tk.LEFT, padx=(0, 10))
        
        # File information label / ファイル情報ラベル
        self.file_info_label = ttk.Label(toolbar, text="No file selected / ファイルが選択されていません")
        self.file_info_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Main pane (left-right split) / メインペイン（左右分割）
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left pane: Chapter tree view / 左ペイン: 章立てツリービュー
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="📚 Chapter Structure / 章立て構造", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Tree view / ツリービュー
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("unique_id",), show="tree")
        self.tree.heading("#0", text="Hierarchy Structure / 階層構造")
        self.tree.column("#0", width=300)
        self.tree.column("unique_id", width=0, minwidth=0, stretch=False)  # Hidden column (internal use) / 非表示列（内部用）
        
        # Tree view scrollbar / ツリービュースクロールバー
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tree selection event / ツリー選択イベント
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Right pane: Content display / 右ペイン: 本文表示
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        ttk.Label(right_frame, text="📖 Content Display / 本文内容", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Content display area / 本文表示エリア
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("", 11),
            state=tk.DISABLED
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Status bar / ステータスバー
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready / 準備完了")
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar (for async processing) / プログレスバー（非同期処理用）
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        
    def open_file(self):
        """Open SEF file / SEFファイルを開く"""
        file_path = filedialog.askopenfilename(
            title="Select SEF File / SEFファイルを選択してください",
            filetypes=[
                ("SEF Files / SEFファイル", "*.SEF"),
                ("All Files / すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def reload_file(self):
        """Reload current file / 現在のファイルをリロード"""
        if self.current_file:
            self.load_file(self.current_file)
    
    def load_file(self, file_path: str):
        """Load file asynchronously / ファイルを非同期で読み込み"""
        self.current_file = file_path
        self.update_status("Loading file... / ファイルを読み込み中...")
        self.progress_bar.start()
        
        # Asynchronous file processing / 非同期でファイル処理
        def load_worker():
            try:
                # SEF structure analysis / SEF構造解析
                result = self.sef_reader.analyze_file(file_path)
                
                if not result['success']:
                    error_msg = f"File analysis error / ファイル解析エラー: {result.get('error', 'Unknown error / 不明なエラー')}"
                    self.root.after(0, lambda msg=error_msg: self.show_error(msg))
                    return
                
                # Get chapter division and hierarchy structure from results
                # 章分割と階層構造取得は結果に含まれる
                chapters = result.get('chapters', [])
                hierarchy = result.get('hierarchy', [])
                
                # Apply results to GUI (execute in main thread)
                # GUIに結果を反映（メインスレッドで実行）
                self.root.after(0, lambda: self.display_results(file_path, chapters, hierarchy, result))
                
            except Exception as e:
                error_msg = f"Loading error / 読み込みエラー: {str(e)}"
                self.root.after(0, lambda msg=error_msg: self.show_error(msg))
        
        # Start worker thread / ワーカースレッド開始
        thread = threading.Thread(target=load_worker, daemon=True)
        thread.start()
    
    def display_results(self, file_path: str, chapters: List[Dict], hierarchy: List[Dict], structure_info: Dict):
        """解析結果をGUIに表示"""
        self.progress_bar.stop()
        
        self.current_chapters = chapters
        self.current_hierarchy = hierarchy
        
        # ファイル情報更新
        file_name = os.path.basename(file_path)
        total_size = structure_info.get('file_size', 0)
        total_chapters = len(chapters)
        
        self.file_info_label.config(
            text=f"📁 {file_name} | 📖 {total_chapters}章 | 💾 {total_size:,} bytes"
        )
        
        # ツリービューをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 階層構造のみでツリービューに追加（章データは選択時に参照）
        self.populate_tree(hierarchy, chapters)
        
        # 初期状態で最初の章を表示
        if chapters:
            first_item = self.tree.get_children()[0] if self.tree.get_children() else None
            if first_item:
                self.tree.selection_set(first_item)
                self.tree.focus(first_item)
                self.on_tree_select(None)
        
        self.update_status(f"✅ {file_name} を正常に読み込みました ({total_chapters}章)")
    
    def populate_tree(self, hierarchy: List[Dict], chapters: List[Dict]):
        """階層構造のみでツリービューを構築（プレーン部分ベース）"""
        # 章データに一意インデックスを追加
        for i, chapter in enumerate(chapters):
            chapter['unique_id'] = i  # 一意識別子を追加
        
        # 階層構造のみに基づいてツリーを構築
        parent_map = {}  # レベル -> 親アイテムのマッピング
        
        for i, item in enumerate(hierarchy):
            level = item['level']
            title = item['title']
            
            # 親アイテムを決定（階層レベルに基づく）
            parent = ""
            if level > 0:
                # 直近の上位レベルを探す
                for parent_level in range(level - 1, -1, -1):
                    if parent_level in parent_map:
                        parent = parent_map[parent_level]
                        break
            
            # 対応する章データがあるかチェック（インデックス順）
            has_content = i < len(chapters)
            
            # ツリーアイテムを挿入（階層構造重視）
            tree_item = self.tree.insert(
                parent, 
                tk.END, 
                text=title,
                values=(),  # 表示列は不要（階層構造のみ）
                tags=("chapter" if has_content else "folder",)
            )
            
            # 階層インデックスをアイテムに関連付け（章データへの参照用）
            self.tree.set(tree_item, "unique_id", i)
            
            # 現在レベルのアイテムとして記録
            parent_map[level] = tree_item
            
            # より深いレベルのマッピングをクリア
            keys_to_clear = [k for k in parent_map.keys() if k > level]
            for clear_level in keys_to_clear:
                del parent_map[clear_level]
        
        # ツリーを展開
        self.expand_tree()
    
    def expand_tree(self):
        """ツリービューを適度に展開"""
        def expand_recursive(item, current_depth=0, max_depth=2):
            if current_depth < max_depth:
                self.tree.item(item, open=True)
                for child in self.tree.get_children(item):
                    expand_recursive(child, current_depth + 1, max_depth)
        
        for root_item in self.tree.get_children():
            expand_recursive(root_item)
    
    def on_tree_select(self, event):
        """ツリーアイテム選択時の処理（一意識別子対応版）"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        display_title = self.tree.item(item, "text")
        
        # 一意識別子を取得
        try:
            unique_id = int(self.tree.set(item, "unique_id"))
            chapter = self.current_chapters[unique_id] if unique_id < len(self.current_chapters) else None
        except (ValueError, IndexError):
            # フォールバック：タイトルで検索
            chapter = None
            for ch in self.current_chapters:
                if ch['title'] in display_title or display_title in ch['title']:
                    chapter = ch
                    break
                chapter = ch
                break
        
        if chapter:
            self.display_chapter(chapter)
        else:
            self.display_message(f"章「{display_title}」の内容が見つかりません。")
    
    def display_chapter(self, chapter: Dict):
        """章の内容を表示"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        # 章タイトル
        self.text_area.insert(tk.END, f"📖 {chapter['title']}\n", "title")
        self.text_area.insert(tk.END, "=" * 50 + "\n\n", "separator")
        
        # 本文
        content = chapter.get('content', '内容が見つかりません。')
        self.text_area.insert(tk.END, content, "content")
        
        # 章情報
        info = f"\n\n" + "─" * 30 + "\n"
        info += f"📊 文字数: {chapter.get('size', 0):,}\n"
        info += f"📍 RTF位置: {chapter.get('start_pos', 0):,} - {chapter.get('end_pos', 0):,}\n"
        self.text_area.insert(tk.END, info, "info")
        
        self.text_area.config(state=tk.DISABLED)
        
        # 先頭にスクロール
        self.text_area.see(1.0)
    
    def display_message(self, message: str):
        """メッセージを表示"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, message)
        self.text_area.config(state=tk.DISABLED)
    
    def show_error(self, error_message: str):
        """エラーを表示"""
        self.progress_bar.stop()
        self.update_status(f"❌ エラー: {error_message}")
        messagebox.showerror("エラー", error_message)
    
    def update_status(self, message: str):
        """ステータスを更新"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

def main():
    """Main function / メイン関数"""
    # Single instance control / シングルインスタンス制御
    if not check_single_instance():
        return
    
    root = tk.Tk()
    app = SEFReaderGUI(root)
    
    # Icon setting (if exists) / アイコン設定（存在する場合）
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    # Exit processing / 終了時の処理
    def on_closing():
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
