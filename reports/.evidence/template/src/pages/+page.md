---
title: Microsoft Copilot Articles Dashboard
description: Analytics dashboard for Microsoft Copilot news articles
---

```sql total_articles_summary
SELECT * FROM memory.duckdb.total_articles_summary
```

```sql copilot_articles_summary
SELECT * FROM memory.duckdb.copilot_articles_summary
```

```sql articles_by_date
SELECT * FROM memory.duckdb.articles_by_date
```

```sql articles_by_source
SELECT * FROM memory.duckdb.articles_by_source
```

```sql recent_articles
SELECT * FROM memory.duckdb.recent_articles
```

## Overview Metrics

<Grid cols=2>
<BigValue 
    data={total_articles_summary} 
    value='total_articles' 
    title='Total Articles'
/>

<BigValue 
    data={copilot_articles_summary} 
    value='copilot_articles' 
    title='Copilot Articles'
/>
</Grid>

## Articles Over Time

<LineChart 
    data={articles_by_date} 
    x=article_date 
    y=total_articles
    title='Total Articles by Date'
/>

<LineChart 
    data={articles_by_date} 
    x=article_date 
    y=copilot_articles
    title='Copilot Articles by Date'
    color='#0078d4'
/>

## Articles by Source

<Grid cols=2>
<BarChart 
    data={articles_by_source}
    x=source_name
    y=total_articles
    swapXY=true
    title='Total Articles by Source'
/>

<BarChart 
    data={articles_by_source}
    x=source_name
    y=copilot_articles
    swapXY=true
    title='Copilot Articles by Source'
    color='#0078d4'
/>
</Grid>

## Recent Articles Summary

<DataTable data={recent_articles} search="true" pageSize=10>
    <Column id="article_date" title="Date" />
    <Column id="source_name" title="Source" />
    <Column id="total_articles" title="Total Articles" />
    <Column id="copilot_articles" title="Copilot Articles" />
</DataTable>
