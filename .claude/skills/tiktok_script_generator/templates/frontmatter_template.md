# Script Frontmatter Template

Every TikTok script file must start with this YAML frontmatter:

```yaml
---
cover: ""
caption: >-
  Short, punchy TikTok caption in German WITH hashtags appended (space-separated, no commas, no quote marks)
published: YYYY-MM-DD
duration: "00:45"
sales:
  - yes
link: ""
tags:
  - "#tag1"
  - "#tag2"
  - "#tag3"
  - "#tag4"
  - "#tag5"
product: "Full Product Name"
source_notes:
  - "product_list/YYYYMMDD/{product_id}/ref_video/video_synthesis.md"
  - "product_list/YYYYMMDD/{product_id}/product_images/image_analysis.md"
  - "product_list/YYYYMMDD/{product_id}/tabcut_data.json"
---
```

## Field Rules

- **`duration`**: Target 00:40–00:50 (standard UGC ad length)
- **`tags`**: Maximum 5 tags, meaningful for commerce/interest discovery
- **`caption`**: Uses YAML block scalar (`>-`) so colons and hashtags don't break parsing
  - Include the same hashtags as `tags` appended at end (space-separated)
  - No commas, no quote marks in hashtag list
- **`source_notes`**: Link to exact reference files used
  - Always include `video_synthesis.md` (critical)
  - Include `image_analysis.md` if visual analysis was used
  - Include `tabcut_data.json` for product metadata
  - Include `fastmoss_data.json` if used as fallback
