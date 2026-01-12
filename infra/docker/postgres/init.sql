-- ============================================
-- DeepResearch 数据库初始化脚本
-- ============================================

-- 启用 pgvector 扩展（用于向量搜索）
CREATE EXTENSION IF NOT EXISTS vector;

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 创建表
-- ============================================

-- 证据表（存储原始数据源）
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_url TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,  -- 'product', 'review', 'article', 'search'
    snippet TEXT,
    html_raw TEXT,
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 向量索引（用于语义去重）
    embedding vector(1536),  -- OpenAI embedding 维度
    
    -- 索引
    CONSTRAINT evidence_source_url_key UNIQUE (source_url)
);

-- 引用表（结论→证据映射）
CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conclusion TEXT NOT NULL,
    evidence_id UUID NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT citations_conclusion_evidence_key UNIQUE (conclusion, evidence_id)
);

-- 调研任务表
CREATE TABLE IF NOT EXISTS research_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword VARCHAR(255) NOT NULL,
    market VARCHAR(10) NOT NULL,
    competitors TEXT[] NOT NULL,  -- 竞品列表
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed
    progress INTEGER DEFAULT 0,  -- 0-100
    result JSONB,  -- 调研结果
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 缓存表（爬虫数据缓存）
CREATE TABLE IF NOT EXISTS scraper_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT scraper_cache_key_unique UNIQUE (cache_key)
);

-- ============================================
-- 创建索引
-- ============================================

-- 证据表索引
CREATE INDEX IF NOT EXISTS idx_evidence_source_type ON evidence(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_extracted_at ON evidence(extracted_at);
CREATE INDEX IF NOT EXISTS idx_evidence_embedding ON evidence USING ivfflat (embedding vector_cosine_ops);

-- 引用表索引
CREATE INDEX IF NOT EXISTS idx_citations_evidence_id ON citations(evidence_id);

-- 调研任务表索引
CREATE INDEX IF NOT EXISTS idx_research_tasks_status ON research_tasks(status);
CREATE INDEX IF NOT EXISTS idx_research_tasks_created_at ON research_tasks(created_at);

-- 缓存表索引
CREATE INDEX IF NOT EXISTS idx_scraper_cache_expires_at ON scraper_cache(expires_at);

-- ============================================
-- 创建触发器（自动更新 updated_at）
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_research_tasks_updated_at 
    BEFORE UPDATE ON research_tasks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 插入测试数据（开发环境）
-- ============================================

-- 仅在开发环境插入测试数据
DO $$
BEGIN
    IF current_database() = 'deep_research' THEN
        -- 插入示例证据
        INSERT INTO evidence (source_url, source_type, snippet, extracted_at)
        VALUES 
            ('https://www.upliftdesk.com/uplift-v2-standing-desk/', 'product', 'UPLIFT V2 Standing Desk - $599', NOW()),
            ('https://www.amazon.com/dp/B07HNKV7J6', 'review', 'Great desk, very stable!', NOW())
        ON CONFLICT (source_url) DO NOTHING;
    END IF;
END $$;

-- ============================================
-- 清理过期缓存的定时任务（可选）
-- ============================================

-- 创建清理函数
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM scraper_cache WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- 注意：实际的定时任务需要使用 pg_cron 扩展或外部调度器

