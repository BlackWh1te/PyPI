"""Migration Generator - AI-powered database migration generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class MigrationGenerator(AdvancedTool):
    """AI-powered database migration generation.
    
    Features:
    - Migration script generation
    - Schema change detection
    - Rollback script generation
    - Data migration strategies
    - Version control integration
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "migration_generator",
            "description": "Generate database migrations with AI-powered analysis",
            "category": ToolCategory.DATABASE,
            "parameters": {
                "type": "object",
                "properties": {
                    "current_schema": {
                        "type": "string",
                        "description": "Current database schema"
                    },
                    "target_schema": {
                        "type": "string",
                        "description": "Target database schema"
                    },
                    "database_type": {
                        "type": "string",
                        "enum": ["postgresql", "mysql", "sqlite", "mongodb", "sqlserver"],
                        "description": "Database type"
                    },
                    "include_rollback": {
                        "type": "boolean",
                        "description": "Include rollback script"
                    },
                    "preserve_data": {
                        "type": "boolean",
                        "description": "Preserve existing data during migration"
                    }
                },
                "required": ["current_schema", "target_schema", "database_type"]
            }
        }
    
    async def execute(
        self,
        current_schema: str,
        target_schema: str,
        database_type: str,
        include_rollback: bool = True,
        preserve_data: bool = True
    ) -> ToolResult:
        """Execute migration generation.
        
        Args:
            current_schema: Current schema
            target_schema: Target schema
            database_type: Database type
            include_rollback: Include rollback
            preserve_data: Preserve data
            
        Returns:
            ToolResult with migration scripts
        """
        prompt = f"""Generate database migration from current to target schema

Database Type: {database_type}
Preserve Data: {preserve_data}

Current Schema:
```
{current_schema}
```

Target Schema:
```
{target_schema}
```

Please provide:
1. Migration script (forward)
2. Rollback script (if requested)
3. Data migration strategy (if preserving data)
4. Risk assessment
5. Execution order
6. Pre-migration checks
7. Post-migration validation
8. Downtime estimation
"""
        
        if include_rollback:
            prompt += "\n9. Rollback procedures and verification"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "database_type": database_type,
                "include_rollback": include_rollback,
                "preserve_data": preserve_data,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Test migrations in staging environment first",
                "Backup database before migration",
                "Use transactional migrations when possible",
                "Document migration steps and rollback procedures"
            ],
            confidence=0.85
        )
