# SEF (Story Editor Format) Technical Specification / SEF（Story Editor Format）技術仕様書

## Abstract / 概要

The **Story Editor Format (SEF)** is a proprietary file format used by Story Editor v3.30 and later versions for storing structured novel data. This document provides a comprehensive technical analysis of the SEF format, including file structure, compression methods, and parsing algorithms.

**Story Editor Format（SEF）**は、Story Editor v3.30以降で使用される構造化小説データ格納用の専用ファイル形式です。本文書では、ファイル構造、圧縮方法、解析アルゴリズムを含むSEF形式の包括的技術解析を提供します。

**Document Version / 文書バージョン**: 1.0  
**Date / 日付**: August 10, 2025 / 2025年8月10日  
**Analysis Scope / 解析範囲**: Multiple SEF format samples from Story Editor v3.30+ / Story Editor v3.30+の複数のSEFフォーマットサンプル  
**Authors / 著者**: Technical Research Team / 技術研究チーム

---

## Table of Contents / 目次

1. [File Structure Overview / ファイル構造概要](#file-structure-overview--ファイル構造概要)
2. [Header Specification / ヘッダー仕様](#header-specification--ヘッダー仕様)
3. [Compression Method / 圧縮方法](#compression-method--圧縮方法)
4. [Data Format / データ形式](#data-format)
5. [Parsing Algorithms / 解析アルゴリズム](#parsing-algorithms--解析アルゴリズム)
6. [Implementation Guidelines / 実装ガイドライン](#implementation-guidelines--実装ガイドライン)
7. [Known Issues and Solutions / 既知の問題と解決策](#known-issues-and-solutions--既知の問題と解決策)
8. [References / 参考文献](#references--参考文献)

---

## File Structure Overview / ファイル構造概要

SEF files employ a three-layer architecture:

SEFファイルは3層構造を採用しています：

```text
[Header Section]         (16 bytes)          [ヘッダーセクション]
[Entry Table]           (variable length)    [エントリーテーブル]
[ZLIB Compressed Data]  (remainder of file)  [ZLIB圧縮データ]
```

### Architecture Design / アーキテクチャ設計

The format is designed for efficient storage of hierarchical novel data with the following characteristics:

この形式は、以下の特性を持つ階層化小説データの効率的格納のために設計されています：

- **Compact Storage / コンパクト格納**: ZLIB compression reduces file size significantly / ZLIB圧縮によりファイルサイズを大幅削減
- **Structured Content / 構造化コンテンツ**: Hierarchical chapter organization / 階層化された章構成
- **Rich Text Support / リッチテキスト対応**: RTF format for formatted content / フォーマット済みコンテンツ用のRTF形式
- **Metadata Preservation / メタデータ保持**: Title, creation date, and other metadata / タイトル、作成日、その他のメタデータ

---

## Header Specification / ヘッダー仕様

### Binary Layout / バイナリレイアウト

The 16-byte header contains essential file metadata:

16バイトのヘッダーには重要なファイルメタデータが含まれています：

| Offset | Size | Field Name | Data Type | Description | 説明 |
|--------|------|------------|-----------|-------------|------|
| 0x00   | 2    | Magic      | uint16_le | Format identifier (0x0303) | フォーマット識別子 |
| 0x02   | 2    | Field1     | uint16_le | Entry count or configuration flags | エントリー数または設定フラグ |
| 0x04   | 4    | Field2     | uint32_le | Data offset or compressed size | データオフセットまたは圧縮サイズ |
| 0x08   | 4    | Field3     | uint32_le | Decompressed size or auxiliary data | 展開後サイズまたは補助データ |
| 0x0C   | 4    | Field4     | uint32_le | Reserved field for future use | 将来使用のための予約フィールド |

### Example Header Analysis / ヘッダー解析例

```text
Magic: 0x0303
Field1: [Entry count or flags]          [エントリー数またはフラグ]
Field2: [Data offset information]       [データオフセット情報]
Field3: [Decompressed size information] [展開後サイズ情報]
Field4: [Reserved field data]           [予約フィールドデータ]
```

---

## Compression Method / 圧縮方法

### ZLIB Implementation / ZLIB実装

SEF files utilize standard ZLIB compression:

SEFファイルは標準的なZLIB圧縮を使用します：

- **Algorithm / アルゴリズム**: DEFLATE (RFC 1951)
- **Wrapper / ラッパー**: ZLIB format (RFC 1950) / ZLIB形式
- **Typical Start Offset / 一般的開始オフセット**: Byte 15 from file beginning / ファイル先頭から15バイト目
- **Header Patterns / ヘッダーパターン**:
  - `0x78 0x01`: Minimal compression / 最小圧縮
  - `0x78 0x9C`: Default compression / デフォルト圧縮
  - `0x78 0xDA`: High compression / 高圧縮
  - `0x78 0x5E`: Maximum compression / 最大圧縮

### Decompression Process / 展開プロセス

```python
import zlib

def decompress_sef_data(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # Standard decompression from offset 15
    compressed_data = data[15:]
    decompressed = zlib.decompress(compressed_data)
    return decompressed
```

---

## Data Format

### Post-Decompression Structure

After decompression, the data contains two distinct sections:

```text
[Plain Text Section]  (Chapter hierarchy)
[RTF Section]        (Formatted content)
```

### Plain Text Section

Contains the hierarchical chapter structure:

- **Encoding**: Shift-JIS
- **Hierarchy Indicator**: Tab characters (`\t`) for indentation
- **Structure Marker**: Lines beginning with `★` for metadata

**Example Structure**:

```text
★ Title ★
Chapter 1
  Section A
    Subsection 1
      Part 1
      Part 2
      Part 3
```

### RTF Section / RTFセクション

Contains the actual content in Rich Text Format:

Rich Text Format形式の実際のコンテンツを含みます：

- **Start Marker / 開始マーカー**: `{\\rtf1`
- **Font Table / フォントテーブル**: Font definitions for proper display / 適切な表示のためのフォント定義
- **Content / コンテンツ**: Novel text with formatting information / 書式情報を含む小説テキスト
- **Structure / 構造**: Multiple RTF documents concatenated / 複数のRTF文書の連結

---

## Parsing Algorithms / 解析アルゴリズム

### Hierarchy-RTF Mapping Algorithm / 階層-RTFマッピングアルゴリズム

The core discovery is that hierarchy items and RTF documents maintain a 1:1 correspondence:

核心的発見は、階層項目とRTF文書が1:1対応を維持していることです：

```python
def parse_sef_with_hierarchy_mapping(decompressed_data):
    """
    Parse SEF data using complete hierarchy-RTF correspondence
    """
    # 1. Decode text data
    text_content = decompressed_data.decode('shift-jis', errors='ignore')
    
    # 2. Split into plain and RTF sections
    rtf_start = text_content.find('{\\rtf')
    plain_section = text_content[:rtf_start]
    rtf_section = text_content[rtf_start:]
    
    # 3. Extract hierarchy structure
    hierarchy = extract_hierarchy(plain_section)
    
    # 4. Extract RTF documents
    rtf_documents = extract_rtf_documents(rtf_section)
    
    # 5. Create 1:1 mapping
    chapters = []
    for i, hierarchy_item in enumerate(hierarchy):
        if i < len(rtf_documents):
            content = rtf_to_plain_text(rtf_documents[i])
            chapters.append({
                'title': hierarchy_item['title'],
                'level': hierarchy_item['level'],
                'content': content,
                'rtf_index': i
            })
    
    return chapters
```

### RTF Document Boundary Detection

Accurate detection of RTF document boundaries using brace counting:

```python
def extract_rtf_documents(rtf_section):
    """
    Extract individual RTF documents with precise boundary detection
    """
    documents = []
    pos = 0
    
    while True:
        # Find next RTF start
        rtf_pos = rtf_section.find('{\\rtf', pos)
        if rtf_pos == -1:
            break
        
        # Count braces to find document end
        brace_count = 0
        doc_pos = rtf_pos
        
        while doc_pos < len(rtf_section):
            char = rtf_section[doc_pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Complete RTF document found
                    rtf_content = rtf_section[rtf_pos:doc_pos + 1]
                    documents.append(rtf_content)
                    break
            doc_pos += 1
        
        pos = rtf_pos + 1
    
    return documents
```

### Hierarchy Extraction

Extract hierarchical structure from plain text section:

```python
def extract_hierarchy(plain_section):
    """
    Extract hierarchical chapter structure
    """
    hierarchy = []
    lines = plain_section.split('\n')
    
    for line in lines:
        stripped_line = line.rstrip()
        if not stripped_line:
            continue
        
        # Calculate indentation level
        level = 0
        for char in line:
            if char == '\t':
                level += 1
            elif char == ' ':
                # Handle 4-space indentation as one level
                level += 0.25
            else:
                break
        
        # Clean title text
        clean_title = line.lstrip('\t ')
        if clean_title and not clean_title.startswith('★'):
            hierarchy.append({
                'title': clean_title,
                'level': int(level)
            })
    
    return hierarchy
```

---

## Implementation Guidelines / 実装ガイドライン

### Text Encoding Handling / テキストエンコーディング処理

SEF files typically use Shift-JIS encoding, but implementations should handle variations:

SEFファイルは通常Shift-JISエンコーディングを使用しますが、実装では変種への対応も必要です：

```python
def decode_sef_text(raw_data):
    """
    Robust text decoding with fallback options
    """
    encodings = ['shift-jis', 'cp932', 'utf-8']
    
    for encoding in encodings:
        try:
            return raw_data.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Final fallback with error handling
    return raw_data.decode('shift-jis', errors='ignore')
```

### RTF to Plain Text Conversion / RTFからプレーンテキストへの変換

Convert RTF content to readable plain text:

RTFコンテンツを読みやすいプレーンテキストに変換します：

```python
def rtf_to_plain_text(rtf_content):
    """
    Convert RTF content to plain text (simplified version)
    RTFコンテンツをプレーンテキストに変換（簡略版）
    """
    if not rtf_content:
        return ""
    
    text = rtf_content
    
    # Decode Shift-JIS hex sequences
    # Shift-JIS16進エンコードシーケンスをデコード
    def decode_sjis_hex_sequence(match):
        hex_sequence = match.group(0)
        hex_pairs = re.findall(r"\\'([0-9a-fA-F]{2})", hex_sequence)
        try:
            byte_array = bytes([int(h, 16) for h in hex_pairs])
            return byte_array.decode('shift_jis', errors='ignore')
        except:
            return ''
    
    text = re.sub(r"(?:\\'[0-9a-fA-F]{2})+", decode_sjis_hex_sequence, text)
    
    # Remove RTF control structures
    # RTF制御構造を除去
    text = re.sub(r'\{\\fonttbl[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', text)
    text = re.sub(r'\{\\colortbl[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', text)
    
    # Remove RTF control commands
    # RTF制御コマンドを除去
    text = re.sub(r'\\[a-zA-Z]+\d+(?:\s+\\[a-zA-Z]+\d+)*', ' ', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    text = re.sub(r'\\[^a-zA-Z]', '', text)
    
    # Remove braces
    # 波括弧を除去
    text = re.sub(r'[{}]', '', text)
    
    # Clean up unnecessary characters and layout numbers
    # 不要な文字とレイアウト関連の数字を整理
    text = re.sub(r';+', ' ', text)  # セミコロンを空白に
    text = re.sub(r'(?<![年月日])[0-9]+(?![年月日])(?:\s+[0-9]+)*\s*', ' ', text)
    
    # Normalize whitespace
    # 空白文字を正規化
    text = text.replace('\\r\\n', '\\n')
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
```

---

## Known Issues and Solutions / 既知の問題と解決策

### Character Encoding Issues / 文字エンコーディングの問題

**Problem / 問題**: Some files may have encoding inconsistencies / 一部のファイルでエンコーディングの不整合が発生する可能性  
**Solution / 解決策**: Implement multi-encoding detection with fallback mechanisms / フォールバック機構付きマルチエンコーディング検出を実装

### Duplicate Chapter Names / 重複章名

**Problem / 問題**: Hierarchy may contain items with identical titles / 階層に同一タイトルの項目が含まれる場合がある  
**Solution / 解決策**: Use index-based identification and display numbering (e.g., "Title (2)") / インデックスベース識別と表示番号付け（例：「タイトル (2)」）を使用

### RTF Parsing Complexity / RTF解析の複雑性

**Problem / 問題**: RTF format contains complex formatting codes / RTF形式には複雑な書式コードが含まれる  
**Solution / 解決策**: Implement robust parser with metadata preservation for important elements / 重要な要素のメタデータ保持機能付きの堅牢なパーサーを実装

### Large File Performance / 大容量ファイルのパフォーマンス

**Problem**: Large SEF files may cause memory issues  
**Solution**: Consider streaming approaches for files exceeding memory limits

---

## Validation Test Cases

### Sample File Structure Analysis

**File Size**: [Decompressed size varies by content]  
**Hierarchy Items**: Variable (typically 3-20 items)  
**RTF Documents**: Equal to hierarchy items  
**Mapping Verification**: Complete 1:1 correspondence confirmed

| Hierarchy Item | Level | RTF Index | Content Type | Typical Size |
|---------------|-------|-----------|--------------|--------------|
| ★ Title ★ | 0 | 0 | Metadata | 50-100 chars |
| Chapter 1 | 0 | 1 | Link/Info | 20-50 chars |
| Section A | 1 | 2 | Link/Info | 20-50 chars |
| Subsection 1 | 1 | 3 | Container | 0-10 chars |
| Part 1 | 2 | 4 | Story content | 1000-5000 chars |
| Part 2 | 2 | 5 | Story content | 1000-5000 chars |
| Part 3 | 2 | 6 | Story content | 1000-5000 chars |

---

## Performance Considerations

### Memory Usage Optimization

For large SEF files:

- Implement streaming decompression
- Use lazy evaluation for chapter content
- Cache frequently accessed data

### Processing Speed

Optimization strategies:

- Pre-compile regular expressions
- Use binary search for RTF boundaries
- Implement parallel processing for multiple files

---

## Future Enhancements

### Proposed Extensions

1. **Write Support**: Enable SEF file creation and modification
2. **Format Conversion**: Support export to standard formats (TXT, EPUB, HTML)
3. **Batch Processing**: Handle multiple SEF files simultaneously  
4. **Search Functionality**: Full-text search within chapter content
5. **Metadata Editing**: Modify title, dates, and other metadata

### Compatibility Goals

- Support for newer Story Editor versions
- Backward compatibility with legacy SEF files
- Cross-platform implementation support

---

## Security Considerations

### Input Validation

When implementing SEF parsers:

- Validate header magic numbers
- Limit decompression size to prevent zip bombs
- Sanitize text content before display
- Implement timeout mechanisms for large files

### Error Handling

Robust error handling strategies:

- Graceful degradation for corrupted files
- Detailed error reporting for debugging
- Recovery mechanisms for partial data

---

## References / 参考文献

1. **ZLIB Specification / ZLIB仕様**: RFC 1950 - ZLIB Compressed Data Format Specification
2. **DEFLATE Specification / DEFLATE仕様**: RFC 1951 - DEFLATE Compressed Data Format Specification  
3. **RTF Specification / RTF仕様**: Microsoft Rich Text Format (RTF) Specification, version 1.9.1
4. **Character Encoding / 文字エンコーディング**: JIS X 0208 and Shift-JIS encoding standards / JIS X 0208およびShift-JISエンコーディング標準

---

## Appendix / 付録

### Sample Implementation / サンプル実装

A reference implementation is available as part of this project:

このプロジェクトの一部として参照実装が利用可能です：

- **File**: Reference implementation included
- **Features**: Complete SEF parsing with GUI interface
- **Dependencies**: Python 3.6+, tkinter
- **License**: Open source

### Test Data

Test SEF files used in this analysis:

- Various sample files from Story Editor applications
- Files with different complexity levels and structures  
- Edge cases for format validation and compatibility testing
- Legacy format samples for backward compatibility verification

---

*This specification document is maintained as part of the SEF Format Analysis project. Updates and revisions are tracked through version control.*
