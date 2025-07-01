# 🔧 TinyRAG Element Variable System RAG Integration Design

## **Problem Statement**

Current TinyRAG architecture has element variables but lacks:
1. UI for dynamic variable input during generation
2. Automatic connection between document chunks and element variables  
3. RAG-based variable population from retrieval results

## **🎯 Enhanced Architecture Solution**

### **Keep Element Variables BUT Enhance Them**

**Answer: YES, keep variables but make them intelligent with automatic RAG integration**

## **1. Enhanced Variable Schema**

```typescript
interface ElementVariable {
  name: string;
  type: VariableType;
  description: string;
  required: boolean;
  source: VariableSource;
  default_value?: any;
  retrieval_config?: RetrievalConfig;
}

enum VariableType {
  TEXT = "text",
  CONTEXT = "context",           // Auto-populated from document chunks
  USER_INPUT = "user_input",     // Manual user input required  
  DOCUMENT_META = "document_meta" // Auto from document metadata
}

enum VariableSource {
  USER_INPUT = "user_input",     // Manual input via UI
  DOCUMENT_RETRIEVAL = "document_retrieval", // Auto from RAG
  PROJECT_CONTEXT = "project_context",       // Auto from project
  COMPUTED = "computed"          // Dynamically computed
}

interface RetrievalConfig {
  query_template: string;        // Template for retrieval query
  max_chunks: number;           // Max chunks to retrieve
  similarity_threshold: number; // Minimum similarity score
  chunk_aggregation: "concat" | "summarize" | "select_best";
}
```

## **2. Automatic Variable Population Service**

```python
class ElementVariableResolver:
    """Service for resolving element variables from multiple sources."""
    
    async def resolve_variables(
        self,
        element: Element,
        user_inputs: Dict[str, Any],
        document_ids: List[str]
    ) -> Dict[str, Any]:
        """Resolve all element variables automatically."""
        
        resolved_variables = {}
        
        for variable in element.template.variables:
            if variable.source == VariableSource.USER_INPUT:
                # Get from user input
                resolved_variables[variable.name] = user_inputs.get(variable.name)
                
            elif variable.source == VariableSource.DOCUMENT_RETRIEVAL:
                # Auto-retrieve from documents
                resolved_variables[variable.name] = await self._resolve_from_documents(
                    variable, document_ids
                )
        
        return resolved_variables
    
    async def _resolve_from_documents(
        self,
        variable: ElementVariable,
        document_ids: List[str]
    ) -> str:
        """Resolve variable from document retrieval."""
        
        # Build retrieval query from variable config
        query = variable.retrieval_config.query_template.format(
            variable_name=variable.name,
            description=variable.description
        )
        
        # Retrieve relevant chunks
        chunks = await self.retrieval_service.retrieve_chunks(
            query=query,
            document_ids=document_ids,
            top_k=variable.retrieval_config.max_chunks
        )
        
        # Aggregate chunks based on strategy
        if variable.retrieval_config.chunk_aggregation == "concat":
            return "\n\n".join([chunk.content for chunk in chunks])
        elif variable.retrieval_config.chunk_aggregation == "select_best":
            return chunks[0].content if chunks else ""
        
        return ""
```

## **3. Enhanced Element Execution Flow**

```python
class EnhancedElementService:
    """Enhanced element service with RAG integration."""
    
    async def execute_element_with_retrieval(
        self,
        element_id: str,
        user_id: str,
        user_inputs: Dict[str, Any] = None,
        document_ids: List[str] = None
    ) -> ElementGeneration:
        """Execute element with automatic variable resolution."""
        
        # 1. Load element
        element = await self.get_element(element_id, user_id)
        
        # 2. Resolve all variables (both user input and auto-retrieved)
        resolved_variables = await self.variable_resolver.resolve_variables(
            element=element,
            user_inputs=user_inputs or {},
            document_ids=document_ids or []
        )
        
        # 3. Substitute variables in template
        populated_prompt = self._substitute_variables(
            element.template.content, resolved_variables
        )
        
        # 4. Execute with LLM
        generation_result = await self.llm_service.generate(populated_prompt)
        
        # 5. Create generation record with full context
        generation = ElementGeneration(
            element_id=element_id,
            user_id=user_id,
            input_data={
                "user_inputs": user_inputs,
                "resolved_variables": resolved_variables,
                "document_ids": document_ids
            },
            generated_content=[GenerationChunk(
                content=generation_result.content,
                source_documents=document_ids or []
            )]
        )
        
        return generation
```

## **4. Frontend Variable Input Interface**

```typescript
const ElementExecutionForm: React.FC = ({ element, projectDocuments }) => {
  const [userInputs, setUserInputs] = useState<Record<string, any>>({});
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  // Separate variables by source
  const userInputVariables = element.template.variables.filter(
    v => v.source === 'user_input'
  );
  
  const contextVariables = element.template.variables.filter(
    v => v.source === 'document_retrieval'
  );

  return (
    <div className="space-y-6">
      {/* Document Selection for Context Variables */}
      <div>
        <h3 className="text-lg font-medium mb-3">Select Documents for Context</h3>
        <DocumentSelector
          documents={projectDocuments}
          selectedIds={selectedDocuments}
          onChange={setSelectedDocuments}
        />
      </div>

      {/* User Input Variables */}
      {userInputVariables.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-3">Required Inputs</h3>
          {userInputVariables.map(variable => (
            <div key={variable.name} className="mb-4">
              <label className="block text-sm font-medium mb-1">
                {variable.name} {variable.required && '*'}
              </label>
              <input
                type="text"
                value={userInputs[variable.name] || ''}
                onChange={(e) => setUserInputs({
                  ...userInputs,
                  [variable.name]: e.target.value
                })}
                className="w-full px-3 py-2 border rounded-lg text-gray-900"
                placeholder={variable.description}
              />
            </div>
          ))}
        </div>
      )}

      {/* Context Variables Preview */}
      {contextVariables.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-3">Auto-Generated Context</h3>
          {contextVariables.map(variable => (
            <div key={variable.name} className="bg-gray-50 p-3 rounded mb-3">
              <div className="font-medium">{variable.name}</div>
              <div className="text-sm text-gray-600">{variable.description}</div>
              <div className="text-xs text-blue-600 mt-1">
                Will be auto-populated from selected documents
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={() => executeElement(userInputs, selectedDocuments)}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg"
      >
        Execute Element
      </button>
    </div>
  );
};
```

## **5. Example Enhanced Element Template**

```json
{
  "name": "Financial Analysis Report Generator",
  "description": "Generates comprehensive financial analysis reports",
  "template": {
    "content": "Generate a financial analysis report for {company_name}.\n\nFinancial Data:\n{financial_data}\n\nMarket Context:\n{market_context}\n\nAnalysis Focus: {analysis_focus}\n\nProvide detailed analysis including trends, ratios, and recommendations.",
    "variables": [
      {
        "name": "company_name",
        "type": "USER_INPUT",
        "source": "user_input",
        "description": "Name of the company to analyze",
        "required": true
      },
      {
        "name": "financial_data", 
        "type": "CONTEXT",
        "source": "document_retrieval",
        "description": "Financial statements and data",
        "required": true,
        "retrieval_config": {
          "query_template": "financial statements earnings revenue profit {company_name}",
          "max_chunks": 5,
          "similarity_threshold": 0.7,
          "chunk_aggregation": "concat"
        }
      },
      {
        "name": "market_context",
        "type": "CONTEXT", 
        "source": "document_retrieval",
        "description": "Market conditions and industry context",
        "required": false,
        "retrieval_config": {
          "query_template": "market conditions industry trends {company_name} sector",
          "max_chunks": 3,
          "similarity_threshold": 0.6,
          "chunk_aggregation": "summarize"
        }
      },
      {
        "name": "analysis_focus",
        "type": "USER_INPUT",
        "source": "user_input", 
        "description": "Specific areas to focus the analysis on",
        "required": false,
        "default_value": "profitability and growth trends"
      }
    ]
  }
}
```

## **6. Enhanced API Endpoints**

```python
@router.post("/{element_id}/execute-enhanced")
async def execute_element_enhanced(
    element_id: str,
    request: EnhancedExecutionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Execute element with automatic variable resolution."""
    
    generation = await element_service.execute_element_with_retrieval(
        element_id=element_id,
        user_id=str(current_user.id),
        user_inputs=request.user_inputs,
        document_ids=request.document_ids
    )
    
    return {
        "generation_id": str(generation.id),
        "status": generation.status,
        "resolved_variables": generation.input_data["resolved_variables"],
        "generated_content": generation.get_full_content()
    }

@router.post("/{element_id}/preview-variables") 
async def preview_element_variables(
    element_id: str,
    request: VariablePreviewRequest
):
    """Preview how variables will be resolved from documents."""
    
    element = await element_service.get_element(element_id)
    preview = await variable_resolver.preview_variable_resolution(
        element, request.document_ids
    )
    
    return {"variable_preview": preview}
```

## **🎯 Key Benefits**

### **1. Intelligent Variable System**
- ✅ **Keep Variables**: Enhanced with automatic sourcing
- ✅ **RAG Integration**: Auto-populate from document retrieval  
- ✅ **Mixed Input**: User inputs + auto-generated context
- ✅ **Flexible Configuration**: Per-variable retrieval settings

### **2. Enhanced User Experience**
- ✅ **Selective Input**: Only input what's truly required
- ✅ **Document Selection**: Choose relevant docs for context
- ✅ **Variable Preview**: See auto-generated content before execution
- ✅ **Smart Defaults**: Intelligent fallbacks and defaults

### **3. Improved Generation Quality**
- ✅ **Relevant Context**: Automatic retrieval ensures relevant info
- ✅ **Consistent Process**: Standardized variable resolution
- ✅ **Rich Metadata**: Track variable sources and resolution

## **📋 Implementation Steps**

### **Phase 1: Backend Enhancement (Week 1)**
1. Update `ElementTemplate` model with enhanced variables
2. Implement `ElementVariableResolver` service
3. Create enhanced execution endpoints
4. Add variable preview functionality

### **Phase 2: Frontend Integration (Week 2)**  
1. Build enhanced element execution UI
2. Add document selection interface
3. Implement variable preview component
4. Update element creation forms

### **Phase 3: Migration & Testing (Week 3)**
1. Migrate existing elements to enhanced format
2. Update pre-built templates with retrieval configs
3. Comprehensive testing with real documents
4. Documentation and examples

## **🎉 Final Answer**

**Should we keep variables?** **YES** - but enhance them significantly:

1. **Enhanced Variable Types**: Support both user input and auto-generated context
2. **RAG Integration**: Automatic population from document retrieval
3. **Intelligent UI**: Dynamic forms based on variable sources  
4. **Flexible Configuration**: Per-variable retrieval settings
5. **Rich Generation Flow**: Complete variable resolution tracking

This architecture bridges the gap between document chunks and element variables, providing both automation and user control where appropriate. 