import logging
from dataclasses import dataclass
from typing import Callable, Dict, Any, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

@dataclass
class RegisteredTool:
    name: str
    func: Callable
    input_schema: Type[BaseModel]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}
        
    def register(self, name: str, func: Callable, input_schema: Type[BaseModel]):
        """Registers a tool statically."""
        if name in self._tools:
            logger.warning(f"Tool {name} is already registered. Overwriting.")
        self._tools[name] = RegisteredTool(name=name, func=func, input_schema=input_schema)
        
    def get_tool(self, name: str) -> RegisteredTool | None:
        return self._tools.get(name)
        
    def execute(self, name: str, args: dict) -> dict:
        """
        Executes a registered tool securely.
        Returns a standardised envelope: {"success": bool, "data": Any, "error": Any}
        """
        logger.info(f"Tool call initiated: {name}")
        
        tool = self.get_tool(name)
        if not tool:
            error_msg = f"Unknown tool: '{name}'"
            logger.error(f"Tool validation failed: {name} - {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": {
                    "code": "UNKNOWN_TOOL",
                    "message": error_msg
                }
            }
            
        # Parse and validate args
        try:
            validated_args = tool.input_schema(**args)
        except ValidationError as e:
            # We don't want to leak full pydantic trace, just extract the first error msg
            errors = e.errors()
            if errors:
                err = errors[0]
                loc = ".".join(str(l) for l in err["loc"])
                msg = f"{loc}: {err['msg']}"
            else:
                msg = str(e)
                
            logger.error(f"Tool validation failed: {name} - {msg}")
            return {
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": msg
                }
            }
            
        # Execute tool
        try:
            # Convert validated model back to dict for kwargs
            result = tool.func(**validated_args.model_dump())
            logger.info(f"Tool call successful: {name}")
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {name} - {str(e)}")
            # Do NOT expose internal stack traces. Only standard message.
            return {
                "success": False,
                "data": None,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e)
                }
            }
