# New Advanced Tools Added

This document summarizes the new advanced tools added to the ai-multitool codebase.

## Overview

Added 26 new tool categories with 26 new advanced tools, expanding the total tool count from 34 to 60.

## New Tools Added

### 1. Performance Analysis Tools (`ai_multitool/advanced/performance/`)

#### PerformanceProfiler
- **File**: `profiler.py`
- **Purpose**: AI-powered performance profiling and optimization
- **Features**:
  - Algorithmic complexity analysis
  - Inefficient data structure detection
  - I/O bottleneck identification
  - Memory access pattern analysis
  - Concurrency issue detection
  - Database query optimization
- **Parameters**: file_path, code, language, focus (cpu/memory/io/algorithm), include_optimizations
- **Use Case**: Optimize slow code, identify performance bottlenecks

### 2. Database Analysis Tools (`ai_multitool/advanced/database/`)

#### SchemaAnalyzer
- **File**: `schema_analyzer.py`
- **Purpose**: AI-powered database schema analysis and optimization
- **Features**:
  - Normalization issue detection
  - Index optimization recommendations
  - Foreign key relationship analysis
  - Data type efficiency checks
  - Query performance implications
  - Schema evolution recommendations
  - Migration script generation
- **Parameters**: schema_file, schema_content, database_type (postgresql/mysql/sqlite/mongodb), focus, include_migrations
- **Use Case**: Optimize database schemas, improve query performance

### 3. API Design Tools (`ai_multitool/advanced/api/`)

#### APIDesigner
- **File**: `designer.py`
- **Purpose**: AI-powered API design with OpenAPI specification generation
- **Features**:
  - Endpoint structure design
  - Request/response schema generation
  - Authentication strategy recommendations
  - Rate limiting design
  - Error handling patterns
  - Versioning strategies
  - OpenAPI/Swagger spec generation
- **Parameters**: description, resources, operations, authentication (api_key/jwt/oauth2/basic), style (rest/graphql/grpc), include_swagger
- **Use Case**: Design RESTful APIs, generate OpenAPI specifications

### 4. Cloud/Container Tools (`ai_multitool/advanced/cloud/`)

#### DockerOptimizer
- **File**: `docker_optimizer.py`
- **Purpose**: AI-powered Docker and docker-compose optimization
- **Features**:
  - Image size optimization
  - Multi-stage build recommendations
  - Layer caching strategies
  - Security best practices
  - Resource limit suggestions
  - Health check configuration
  - Network configuration optimization
- **Parameters**: dockerfile_path, dockerfile_content, compose_file, focus (size/security/performance), include_multistage
- **Use Case**: Optimize Docker images, reduce container size, improve security

### 5. Logging/Debugging Tools (`ai_multitool/advanced/logging/`)

#### LogAnalyzer
- **File**: `analyzer.py`
- **Purpose**: AI-powered log analysis with anomaly detection
- **Features**:
  - Error pattern detection
  - Performance bottleneck identification
  - Security incident detection
  - Root cause analysis
  - Trend analysis
  - Alert recommendations
  - Recurring pattern identification
- **Parameters**: log_file, log_content, log_format (json/text/syslog/apache/nginx), time_range, focus (errors/performance/security/anomalies), include_patterns
- **Use Case**: Debug production issues, analyze log files, detect anomalies

### 6. Machine Learning Tools (`ai_multitool/advanced/ml/`)

#### ModelOptimizer
- **File**: `model_optimizer.py`
- **Purpose**: AI-powered ML model optimization
- **Features**:
  - Hyperparameter tuning suggestions
  - Architecture improvements
  - Training efficiency optimization
  - Inference optimization
  - Model compression
  - Feature engineering recommendations
  - Data preprocessing suggestions
  - Quantization techniques
- **Parameters**: model_code, model_file, framework (pytorch/tensorflow/sklearn/xgboost), task_type (classification/regression/nlp/cv), focus (hyperparameters/architecture/training/inference), include_quantization
- **Use Case**: Optimize ML models, improve training speed, reduce model size

### 7. DevOps Tools (`ai_multitool/advanced/devops/`)

#### PipelineAnalyzer
- **File**: `pipeline_analyzer.py`
- **Purpose**: AI-powered CI/CD pipeline analysis and optimization
- **Features**:
  - Build optimization recommendations
  - Test strategy improvement
  - Deployment safety checks
  - Pipeline efficiency analysis
  - Security best practices
  - Cost optimization
  - Parallelization opportunities
  - Caching strategies
- **Parameters**: pipeline_file, pipeline_content, platform (github/gitlab/jenkins/circleci/azure), focus (performance/security/cost/reliability), include_caching
- **Use Case**: Optimize CI/CD pipelines, reduce build times, improve deployment reliability

### 8. Monitoring Tools (`ai_multitool/advanced/monitoring/`)

#### AlertOptimizer
- **File**: `alert_optimizer.py`
- **Purpose**: AI-powered monitoring and alerting optimization
- **Features**:
  - Alert fatigue reduction
  - Threshold optimization
  - Metric selection guidance
  - Dashboard design recommendations
  - Incident response strategies
  - Alert routing optimization
  - Notification strategy improvements
- **Parameters**: alert_config, metrics, current_issues, platform (prometheus/datadog/grafana/cloudwatch/newrelic), focus (thresholds/metrics/routing/fatigue)
- **Use Case**: Reduce alert noise, improve monitoring effectiveness, optimize alert thresholds

### 9. Mobile Tools (`ai_multitool/advanced/mobile/`)

#### MobileAppAnalyzer
- **File**: `app_analyzer.py`
- **Purpose**: AI-powered mobile app analysis for performance and UX
- **Features**:
  - Performance optimization
  - Battery usage analysis
  - Memory management
  - UI/UX improvements
  - App size optimization
  - Network efficiency
  - Platform-specific best practices
- **Parameters**: app_code, app_file, platform (ios/android/flutter/react_native), focus (performance/battery/memory/ux/size), include_platform_specific
- **Use Case**: Optimize mobile apps, reduce battery drain, improve user experience

### 10. Frontend Tools (`ai_multitool/advanced/frontend/`)

#### ComponentAnalyzer
- **File**: `component_analyzer.py`
- **Purpose**: AI-powered frontend component analysis
- **Features**:
  - Performance optimization
  - Accessibility improvements (WCAG)
  - Responsive design analysis
  - State management optimization
  - Component reusability
  - Bundle size optimization
  - SEO considerations
- **Parameters**: component_code, component_file, framework (react/vue/angular/svelte), focus (performance/accessibility/responsive/reusability/bundle), include_a11y
- **Use Case**: Optimize frontend components, improve accessibility, reduce bundle size

### 11. Crypto Tools (`ai_multitool/advanced/crypto/`)

#### CryptoKeyManager
- **File**: `key_manager.py`
- **Purpose**: AI-powered cryptographic key management advisor
- **Features**:
  - Key generation best practices
  - Key rotation strategies
  - Encryption algorithm selection
  - Key storage security
  - Certificate management
  - Key lifecycle management
  - Compliance requirements (GDPR, PCI-DSS)
- **Parameters**: use_case, data_type (symmetric/asymmetric/hashing/signing), compliance, focus (generation/rotation/storage/algorithms), include_examples
- **Use Case**: Implement secure key management, ensure compliance, select appropriate encryption

### 12. Network Tools (`ai_multitool/advanced/network/`)

#### NetworkProtocolAnalyzer
- **File**: `protocol_analyzer.py`
- **Purpose**: AI-powered network protocol and API optimization
- **Features**:
  - Protocol selection guidance
  - Data serialization optimization
  - Compression strategies
  - Caching policies
  - Rate limiting design
  - Security considerations
  - Latency optimization
- **Parameters**: api_spec, protocol (http/grpc/websocket/mqtt), data_format (json/protobuf/xml/msgpack), focus (performance/security/bandwidth/latency), include_compression
- **Use Case**: Optimize network protocols, reduce bandwidth, improve API performance

### 13. Data Tools (`ai_multitool/advanced/data/`)

#### DataPipelineOptimizer
- **File**: `pipeline_optimizer.py`
- **Purpose**: AI-powered data pipeline optimization
- **Features**:
  - ETL optimization
  - Data quality checks
  - Schema evolution
  - Partitioning strategies
  - Incremental processing
  - Data lineage
  - Cost optimization
- **Parameters**: pipeline_code, pipeline_file, framework (airflow/dbt/spark/pandas), focus (performance/quality/cost/reliability), include_quality_checks
- **Use Case**: Optimize data pipelines, improve data quality, reduce processing costs

### 14. Web Tools (`ai_multitool/advanced/web/`)

#### WebScraper
- **File**: `scraper.py`
- **Purpose**: AI-powered web scraping with selector generation
- **Features**:
  - Data extraction strategies
  - CSS/XPath selector generation
  - Anti-scraping evasion
  - Rate limiting design
  - Data cleaning
  - Storage strategies
- **Parameters**: url, html_content, data_target, focus (selectors/anti_bot/cleaning/storage), include_code
- **Use Case**: Scrape web data, generate selectors, avoid anti-bot measures

### 15. SEO Tools (`ai_multitool/advanced/seo/`)

#### SEOOptimizer
- **File**: `optimizer.py`
- **Purpose**: AI-powered SEO optimization
- **Features**:
  - Keyword optimization
  - Meta tag analysis
  - Content structure
  - Readability
  - Internal linking
  - Technical SEO
  - Performance impact
- **Parameters**: content, url, keywords, focus (keywords/technical/content/performance), include_suggestions
- **Use Case**: Optimize web pages for search engines, improve rankings

### 16. Accessibility Tools (`ai_multitool/advanced/accessibility/`)

#### AccessibilityAuditor
- **File**: `auditor.py`
- **Purpose**: AI-powered accessibility auditing (WCAG compliance)
- **Features**:
  - WCAG compliance checking
  - Screen reader compatibility
  - Keyboard navigation
  - Color contrast
  - Alt text analysis
  - ARIA attributes
  - Focus management
- **Parameters**: html_content, component_code, wcag_level (A/AA/AAA), focus (contrast/keyboard/screen_reader/aria), include_fixes
- **Use Case**: Audit accessibility, ensure WCAG compliance, improve screen reader support

### 17. Backup Tools (`ai_multitool/advanced/backup/`)

#### BackupStrategy
- **File**: `strategy.py`
- **Purpose**: AI-powered backup strategy design
- **Features**:
  - Backup frequency
  - Retention policies
  - Storage optimization
  - Recovery testing
  - Disaster recovery
  - Encryption strategies
  - Cost optimization
- **Parameters**: data_type, data_size, rpo (Recovery Point Objective), rto (Recovery Time Objective), focus (frequency/storage/recovery/cost), include_encryption
- **Use Case**: Design backup strategies, plan disaster recovery, optimize backup costs

### 18. Analytics Tools (`ai_multitool/advanced/analytics/`)

#### AnalyticsReporter
- **File**: `reporter.py`
- **Purpose**: AI-powered analytics reporting and dashboard design
- **Features**:
  - Report generation
  - Dashboard design
  - KPI selection
  - Data visualization
  - Trend analysis
  - Anomaly detection
  - Insight generation
- **Parameters**: data_description, metrics, goal, focus (kpis/visualization/insights/dashboard), include_sql
- **Use Case**: Generate analytics reports, design dashboards, select KPIs

### 19. Automation Tools (`ai_multitool/advanced/automation/`)

#### WorkflowDesigner
- **File**: `workflow.py`
- **Purpose**: AI-powered workflow automation design
- **Features**:
  - Workflow design
  - Automation opportunities
  - Task dependencies
  - Error handling
  - Retry strategies
  - Notification triggers
  - Integration points
- **Parameters**: process_description, steps, tools, focus (dependencies/error_handling/triggers/integration), include_diagram
- **Use Case**: Design automated workflows, map dependencies, plan automation

### 20. Compliance Tools (`ai_multitool/advanced/compliance/`)

#### ComplianceAuditor
- **File**: `auditor.py`
- **Purpose**: AI-powered compliance auditing
- **Features**:
  - GDPR compliance
  - HIPAA compliance
  - SOC 2 compliance
  - PCI-DSS compliance
  - Data retention
  - Privacy policies
  - Audit trails
  - Risk assessment
- **Parameters**: system_description, standards (GDPR/HIPAA/SOC2/PCI-DSS), data_type, focus (data_privacy/security/audit_trail/risk), include_checklist
- **Use Case**: Audit compliance, ensure GDPR/HIPAA compliance, generate checklists

### 21. Infrastructure Tools (`ai_multitool/advanced/infrastructure/`)

#### InfrastructureProvisioner
- **File**: `provisioner.py`
- **Purpose**: AI-powered infrastructure provisioning
- **Features**:
  - Resource sizing
  - Cost optimization
  - High availability
  - Scalability
  - Security groups
  - Network design
  - Multi-region strategy
- **Parameters**: service_type, expected_load, provider (aws/gcp/azure), focus (cost/ha/scalability/security), include_terraform
- **Use Case**: Provision cloud infrastructure, optimize costs, ensure high availability

### 22. Messaging Tools (`ai_multitool/advanced/messaging/`)

#### QueueAnalyzer
- **File**: `queue_analyzer.py`
- **Purpose**: AI-powered message queue analysis
- **Features**:
  - Queue configuration
  - Message ordering
  - Dead letter queues
  - Retry policies
  - Throughput optimization
  - Consumer scaling
  - Backpressure handling
- **Parameters**: queue_type (rabbitmq/kafka/sqs/redis), message_type, throughput, focus (configuration/retry/scaling/ordering), include_examples
- **Use Case**: Optimize message queues, improve throughput, handle backpressure

### 23. Storage Tools (`ai_multitool/advanced/storage/`)

#### StorageOptimizer
- **File**: `optimizer.py`
- **Purpose**: AI-powered storage optimization
- **Features**:
  - Storage tier selection
  - Compression strategies
  - Lifecycle policies
  - Access patterns
  - Cost optimization
  - Performance tuning
  - Data archiving
- **Parameters**: data_type, access_pattern (hot/warm/cold/mixed), provider (s3/gcs/azure), focus (cost/performance/lifecycle/compression), include_policy
- **Use Case**: Optimize storage costs, implement lifecycle policies, select appropriate tiers

### 24. Search Tools (`ai_multitool/advanced/search/`)

#### SearchAnalyzer
- **File**: `analyzer.py`
- **Purpose**: AI-powered search and indexing analysis
- **Features**:
  - Search schema design
  - Indexing strategy
  - Query optimization
  - Relevance tuning
  - Faceted search
  - Synonyms handling
  - Spell correction
- **Parameters**: data_description, search_engine (elasticsearch/solr/algolia), query_types, focus (schema/indexing/query/relevance), include_mapping
- **Use Case**: Design search schemas, optimize queries, improve relevance

### 25. Email Tools (`ai_multitool/advanced/email/`)

#### EmailAnalyzer
- **File**: `analyzer.py`
- **Purpose**: AI-powered email analysis
- **Features**:
  - Content optimization
  - Deliverability
  - Spam prevention
  - Personalization
  - A/B testing
  - Template design
  - Engagement tracking
- **Parameters**: email_content, email_type (marketing/transactional/notification/newsletter), focus (deliverability/content/personalization/design), include_subject
- **Use Case**: Optimize email campaigns, improve deliverability, prevent spam

### 26. Legal Tools (`ai_multitool/advanced/legal/`)

#### ContractAnalyzer
- **File**: `contract_analyzer.py`
- **Purpose**: AI-powered legal contract analysis
- **Features**:
  - Contract clauses
  - Risk identification
  - Compliance checks
  - Terms negotiation
  - Liability assessment
  - Jurisdiction issues
  - Standard clauses
- **Parameters**: contract_text, contract_type, jurisdiction, focus (risks/compliance/terms/liability), include_suggestions
- **Use Case**: Analyze contracts, identify risks, ensure compliance

### 27. IoT Tools (`ai_multitool/advanced/iot/`)

#### IoTDeviceManager
- **File**: `device_manager.py`
- **Purpose**: AI-powered IoT device management
- **Features**:
  - Device provisioning
  - Firmware updates
  - Security policies
  - Data collection
  - Edge computing
  - Power management
  - Telemetry
- **Parameters**: device_type, deployment_scale, connectivity (wifi/cellular/lora/mqtt), focus (security/power/connectivity/telemetry), include_architecture
- **Use Case**: Manage IoT devices, optimize power consumption, secure firmware updates

## Tool Statistics

| Category | Previous Count | New Count | Total |
|----------|----------------|-----------|-------|
| Code Analysis | 5 | 0 | 5 |
| Git Operations | 4 | 0 | 4 |
| RAG | 4 | 0 | 4 |
| AI Features | 4 | 0 | 4 |
| Security | 3 | 0 | 3 |
| Testing | 3 | 0 | 3 |
| Documentation | 3 | 0 | 3 |
| Project Analysis | 3 | 0 | 3 |
| Collaboration | 3 | 0 | 3 |
| File Operations | 2 | 0 | 2 |
| **Performance** | 0 | 1 | 1 |
| **Database** | 0 | 1 | 1 |
| **API** | 0 | 1 | 1 |
| **Cloud** | 0 | 1 | 1 |
| **Logging** | 0 | 1 | 1 |
| **ML** | 0 | 1 | 1 |
| **DevOps** | 0 | 1 | 1 |
| **Monitoring** | 0 | 1 | 1 |
| **Mobile** | 0 | 1 | 1 |
| **Frontend** | 0 | 1 | 1 |
| **Crypto** | 0 | 1 | 1 |
| **Network** | 0 | 1 | 1 |
| **Data** | 0 | 1 | 1 |
| **Web** | 0 | 1 | 1 |
| **SEO** | 0 | 1 | 1 |
| **Accessibility** | 0 | 1 | 1 |
| **Backup** | 0 | 1 | 1 |
| **Analytics** | 0 | 1 | 1 |
| **Automation** | 0 | 1 | 1 |
| **Compliance** | 0 | 1 | 1 |
| **Infrastructure** | 0 | 1 | 1 |
| **Messaging** | 0 | 1 | 1 |
| **Storage** | 0 | 1 | 1 |
| **Search** | 0 | 1 | 1 |
| **Email** | 0 | 1 | 1 |
| **Legal** | 0 | 1 | 1 |
| **IoT** | 0 | 1 | 1 |
| **TOTAL** | 34 | 26 | 60 |

## Implementation Details

All new tools follow the established pattern:
- Inherit from `AdvancedTool` base class
- Implement `get_tool_definition()` for tool registration
- Implement `execute()` with async support
- Return standardized `ToolResult` with metrics, suggestions, and confidence scores
- Include comprehensive docstrings
- Support both file-based and direct content input
- Provide JSON-structured AI responses

## Usage Examples

```python
from ai_multitool.advanced.performance.profiler import PerformanceProfiler
from ai_multitool.advanced.database.schema_analyzer import SchemaAnalyzer
from ai_multitool.advanced.api.designer import APIDesigner
from ai_multitool.advanced.devops.pipeline_analyzer import PipelineAnalyzer
from ai_multitool.advanced.monitoring.alert_optimizer import AlertOptimizer
from ai_multitool.advanced.mobile.app_analyzer import MobileAppAnalyzer
from ai_multitool.advanced.frontend.component_analyzer import ComponentAnalyzer
from ai_multitool.advanced.crypto.key_manager import CryptoKeyManager
from ai_multitool.advanced.network.protocol_analyzer import NetworkProtocolAnalyzer
from ai_multitool.advanced.data.pipeline_optimizer import DataPipelineOptimizer
from ai_multitool.advanced.web.scraper import WebScraper
from ai_multitool.advanced.seo.optimizer import SEOOptimizer
from ai_multitool.advanced.accessibility.auditor import AccessibilityAuditor
from ai_multitool.advanced.backup.strategy import BackupStrategy
from ai_multitool.advanced.analytics.reporter import AnalyticsReporter
from ai_multitool.advanced.automation.workflow import WorkflowDesigner
from ai_multitool.advanced.compliance.auditor import ComplianceAuditor
from ai_multitool.advanced.infrastructure.provisioner import InfrastructureProvisioner
from ai_multitool.advanced.messaging.queue_analyzer import QueueAnalyzer
from ai_multitool.advanced.storage.optimizer import StorageOptimizer
from ai_multitool.advanced.search.analyzer import SearchAnalyzer
from ai_multitool.advanced.email.analyzer import EmailAnalyzer
from ai_multitool.advanced.legal.contract_analyzer import ContractAnalyzer
from ai_multitool.advanced.iot.device_manager import IoTDeviceManager

# Performance profiling
profiler = PerformanceProfiler(llm_client=client)
result = await profiler.execute(
    file_path="app.py",
    focus="cpu",
    include_optimizations=True
)

# Schema analysis
analyzer = SchemaAnalyzer(llm_client=client)
result = await analyzer.execute(
    schema_file="schema.sql",
    database_type="postgresql",
    focus="performance"
)

# API design
designer = APIDesigner(llm_client=client)
result = await designer.execute(
    description="E-commerce API for product management",
    resources=["products", "orders", "users"],
    operations=["create", "read", "update", "delete"],
    authentication="jwt",
    include_swagger=True
)

# CI/CD pipeline analysis
pipeline_analyzer = PipelineAnalyzer(llm_client=client)
result = await pipeline_analyzer.execute(
    pipeline_file=".github/workflows/ci.yml",
    platform="github",
    focus="performance",
    include_caching=True
)

# Alert optimization
alert_optimizer = AlertOptimizer(llm_client=client)
result = await alert_optimizer.execute(
    metrics=["cpu_usage", "memory_usage", "response_time"],
    current_issues="too many false positives at night",
    platform="prometheus",
    focus="fatigue"
)

# Mobile app analysis
mobile_analyzer = MobileAppAnalyzer(llm_client=client)
result = await mobile_analyzer.execute(
    app_file="MainActivity.kt",
    platform="android",
    focus="battery",
    include_platform_specific=True
)

# Frontend component analysis
component_analyzer = ComponentAnalyzer(llm_client=client)
result = await component_analyzer.execute(
    component_file="Button.tsx",
    framework="react",
    focus="accessibility",
    include_a11y=True
)

# Crypto key management
crypto_manager = CryptoKeyManager(llm_client=client)
result = await crypto_manager.execute(
    use_case="encrypting user data at rest",
    data_type="symmetric",
    compliance=["GDPR", "PCI-DSS"],
    focus="algorithms",
    include_examples=True
)

# Network protocol analysis
network_analyzer = NetworkProtocolAnalyzer(llm_client=client)
result = await network_analyzer.execute(
    protocol="grpc",
    data_format="protobuf",
    focus="bandwidth",
    include_compression=True
)

# Data pipeline optimization
data_optimizer = DataPipelineOptimizer(llm_client=client)
result = await data_optimizer.execute(
    pipeline_file="etl_job.py",
    framework="pandas",
    focus="quality",
    include_quality_checks=True
)

# Web scraping
scraper = WebScraper(llm_client=client)
result = await scraper.execute(
    target_url="https://example.com",
    data_type="product_listings",
    focus="selectors",
    include_code=True
)

# SEO optimization
seo_optimizer = SEOOptimizer(llm_client=client)
result = await seo_optimizer.execute(
    page_content="<html>...</html>",
    page_type="product",
    focus="keywords",
    include_suggestions=True
)

# Accessibility auditing
a11y_auditor = AccessibilityAuditor(llm_client=client)
result = await a11y_auditor.execute(
    page_content="<html>...</html>",
    standard="WCAG",
    level="AA",
    focus="contrast",
    include_fixes=True
)

# Backup strategy
backup_strategy = BackupStrategy(llm_client=client)
result = await backup_strategy.execute(
    data_description="PostgreSQL database with 1TB data",
    rpo="1h",
    rto="4h",
    focus="cost",
    include_script=True
)

# Analytics reporting
analytics_reporter = AnalyticsReporter(llm_client=client)
result = await analytics_reporter.execute(
    metrics_data="sales, users, revenue",
    dashboard_type="executive",
    focus="visualization",
    include_dashboard=True
)

# Workflow automation
workflow_designer = WorkflowDesigner(llm_client=client)
result = await workflow_designer.execute(
    process_description="User onboarding with email verification",
    steps=["register", "verify_email", "complete_profile"],
    tools=["email", "database", "analytics"],
    focus="error_handling",
    include_diagram=True
)

# Compliance auditing
compliance_auditor = ComplianceAuditor(llm_client=client)
result = await compliance_auditor.execute(
    system_description="E-commerce platform with user data",
    standards=["GDPR", "PCI-DSS"],
    data_type="user_personal",
    focus="data_privacy",
    include_checklist=True
)

# Infrastructure provisioning
infra_provisioner = InfrastructureProvisioner(llm_client=client)
result = await infra_provisioner.execute(
    service_type="web_application",
    expected_load="10000 users/day",
    provider="aws",
    focus="cost",
    include_terraform=True
)

# Queue analysis
queue_analyzer = QueueAnalyzer(llm_client=client)
result = await queue_analyzer.execute(
    queue_type="rabbitmq",
    message_type="order_events",
    throughput="1000 msg/min",
    focus="retry",
    include_examples=True
)

# Storage optimization
storage_optimizer = StorageOptimizer(llm_client=client)
result = await storage_optimizer.execute(
    data_type="user_uploads",
    access_pattern="warm",
    provider="s3",
    focus="cost",
    include_policy=True
)

# Search analysis
search_analyzer = SearchAnalyzer(llm_client=client)
result = await search_analyzer.execute(
    data_description="Product catalog with 1M items",
    search_engine="elasticsearch",
    query_types=["full_text", "filter", "autocomplete"],
    focus="schema",
    include_mapping=True
)

# Email analysis
email_analyzer = EmailAnalyzer(llm_client=client)
result = await email_analyzer.execute(
    email_content="Welcome to our service...",
    email_type="transactional",
    focus="deliverability",
    include_subject=True
)

# Contract analysis
contract_analyzer = ContractAnalyzer(llm_client=client)
result = await contract_analyzer.execute(
    contract_text="SERVICE AGREEMENT...",
    contract_type="service",
    jurisdiction="US",
    focus="risks",
    include_suggestions=True
)

# IoT device management
iot_manager = IoTDeviceManager(llm_client=client)
result = await iot_manager.execute(
    device_type="sensor",
    deployment_scale="1000 devices",
    connectivity="mqtt",
    focus="security",
    include_architecture=True
)
```

## Benefits

1. **Expanded Coverage**: New categories cover performance, databases, APIs, cloud, logging, ML, DevOps, monitoring, mobile, frontend, crypto, network, data engineering, web, SEO, accessibility, backup, analytics, automation, compliance, infrastructure, messaging, storage, search, email, legal, and IoT
2. **Comprehensive Toolset**: 60 total tools across 30+ categories covering the entire software development lifecycle
3. **Consistent Interface**: All tools follow the same pattern for easy integration
4. **AI-Powered**: Leverages LLM for intelligent analysis and recommendations
5. **Structured Output**: Standardized ToolResult format with metrics and suggestions
6. **Flexible Input**: Supports both file paths and direct content
7. **Focus Options**: Each tool allows focusing on specific aspects
8. **Platform Support**: Multi-platform support (iOS, Android, React, Vue, etc.)
9. **Compliance Ready**: Built-in compliance considerations (GDPR, PCI-DSS, WCAG)
10. **Cost Optimization**: Many tools include cost-saving recommendations
11. **Token Budget Controls**: Built-in token budget tracking and limits to prevent overspending
12. **Session Management**: Token usage tracking across tool executions with configurable limits

## Future Enhancements

Potential additions for each new category:
- **Performance**: Memory profiler, concurrency analyzer, GPU optimization
- **Database**: Query optimizer, migration generator, data replication
- **API**: API tester, mock server generator, API versioning
- **Cloud**: Kubernetes optimizer, Terraform analyzer, cost estimator
- **Logging**: Log formatter, alert rule generator, log aggregation
- **ML**: Data profiler, feature importance analyzer, model monitoring
- **DevOps**: Infrastructure as Code analyzer, deployment strategist
- **Monitoring**: Dashboard designer, SLA calculator, incident predictor
- **Mobile**: Battery profiler, network analyzer, crash analyzer
- **Frontend**: SEO analyzer, performance auditor, accessibility tester
- **Crypto**: Certificate manager, HSM integration, key rotation scheduler
- **Network**: Load balancer optimizer, CDN selector, firewall rule analyzer
- **Data**: Data catalog generator, lineage visualizer, quality dashboard
