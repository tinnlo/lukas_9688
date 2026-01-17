"""
Strategic Analysis (Phase 3C).

Analyzes target audience, psychological triggers, market fit, and replication strategy.
"""

import subprocess
from pathlib import Path
from loguru import logger

from ..models import VideoMetadata, TranscriptData, sanitize_gemini_output


def analyze_strategic(
    metadata: VideoMetadata,
    transcript: TranscriptData,
    structural_analysis: str,
    content_analysis: str
) -> str:
    """
    Perform strategic analysis using Gemini (Phase 3C).

    Args:
        metadata: Video metadata
        transcript: Transcription data
        structural_analysis: Output from Phase 3A
        content_analysis: Output from Phase 3B

    Returns:
        Strategic analysis markdown
    """
    logger.info("=== Phase 3C: Strategic Analysis ===")

    # Context summary (truncated to fit token limits)
    context = f"""**Structural Context:**
{structural_analysis[:400]}...

**Content Context:**
{content_analysis[:400]}...

**Transcript:**
{transcript.text[:300]}...
"""

    prompt = f"""You are a TikTok marketing strategist analyzing this video for replication.

**Video Performance:**
- Creator: {metadata.creator}
- Views: {metadata.views or 'Unknown'}
- Likes: {metadata.likes or 'Unknown'}
- Duration: {metadata.duration:.1f}s
- Language: {transcript.language}

{context}

---

**Task: Strategic analysis for replication**

**CRITICAL: Output EVERYTHING in BILINGUAL format - English first, then Chinese translation**

Output in Markdown with bilingual headers (English | 中文):

## Target Audience | 目标受众

**Demographics | 人口统计:**
- Age range | 年龄范围: [e.g., 25-40]
- Gender | 性别: [Primary/Secondary] | [主要/次要]
- Location | 地点: [Germany, specific regions?] | [德国，特定地区]
- Income level | 收入水平: [Low/Middle/High] | [低/中/高]

**Psychographics | 心理特征:**
- Pain points this video addresses | 视频解决的痛点
- Values and priorities | 价值观和优先级
- Lifestyle indicators | 生活方式指标
- Decision-making triggers | 决策触发因素

**Evidence | 证据:**
[What in the video signals this audience?] | [视频中哪些信号表明该受众？]

## Psychological Triggers | 心理触发器

Identify which triggers are used | 识别使用的触发器:

1. **[Trigger Name] | [触发器名称]** (e.g., FOMO, Social Proof, Authority)
   - How it's used | 如何使用: [Specific example] | [具体示例]
   - Effectiveness | 有效性: [1-10]

2. **[Trigger Name] | [触发器名称]**
   - How it's used | 如何使用: [Specific example] | [具体示例]
   - Effectiveness | 有效性: [1-10]

## Germany Market Fit | 德国市场适配度

- **Cultural Alignment | 文化契合度:** [Score 1-10]
  - [Why it works/doesn't work for German audience] | [为什么对德国受众有效/无效]

- **Language Style | 语言风格:**
  - Formal vs Casual | 正式vs随意: [Analysis] | [分析]
  - Local phrases | 本地表达: [Examples] | [示例]

- **Visual Style | 视觉风格:**
  - German preferences | 德国偏好: [How well it matches] | [匹配程度]

## Replication Blueprint | 复制蓝图

### 🟢 COPY EXACTLY | 完全复制 (Core Elements | 核心元素)
- **[Element 1]:** [Why it's critical] | [为什么关键]
- **[Element 2]:** [Why it's critical] | [为什么关键]
- **[Element 3]:** [Why it's critical] | [为什么关键]

### 🟡 ADAPT | 调整 (Customize | 定制)
- **[Element 1]:** [How to adapt for your product] | [如何为产品调整]
- **[Element 2]:** [How to adapt for your product] | [如何为产品调整]

### 🔴 AVOID | 避免 (Risks | 风险)
- **[Element 1]:** [Why it's risky to copy] | [为什么有风险]
- **[Element 2]:** [Why it's risky to copy] | [为什么有风险]

## Production Requirements | 制作要求

**Budget Estimate | 预算估算:** [Low €50-200 / Medium €200-1000 / High €1000+]

**Equipment Needed | 所需设备:**
- Camera | 相机: [e.g., iPhone 14 Pro or better]
- Lighting | 灯光: [Natural/Ring light/Professional] | [自然/环形灯/专业]
- Audio | 音频: [Built-in mic/Lavalier/Professional] | [内置/领夹式/专业]
- Editing | 剪辑: [Basic/Intermediate/Advanced] | [基础/中级/高级]

**Talent Requirements | 演员要求:**
- On-camera person | 出镜人员: [Age, gender, skills] | [年龄、性别、技能]
- Voice actor | 配音演员: [Native {transcript.language} speaker] | [母语人士]
- Skill level | 技能水平: [Beginner/Intermediate/Professional] | [初学者/中级/专业]

**Timeline Estimate | 时间估算:** [X days for production] | [制作需要X天]

**Be strategic and actionable for exact replication. | 内容需具有战略性且可操作，便于精确复制。**
"""

    # No frames needed for strategic analysis - text only
    cmd = [
        "gemini",
        "-o", "text",
        "-m", "gemini-3-pro-preview",
        prompt
    ]

    logger.info("Calling Gemini for strategic analysis...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            check=True
        )

        analysis = result.stdout
        analysis = sanitize_gemini_output(analysis)

        logger.success(f"Strategic analysis complete ({len(analysis)} chars)")
        return analysis

    except subprocess.CalledProcessError as e:
        logger.warning(f"Trying flash model: {e.stderr[:100]}")
        cmd[4] = "gemini-3-flash-preview"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=True)
            analysis = sanitize_gemini_output(result.stdout)
            logger.success("Strategic analysis complete (fallback)")
            return analysis
        except Exception as e2:
            raise RuntimeError(f"Strategic analysis failed: {e2}")
