"""
Prompt 模板管理 API 路由
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from pathlib import Path
import json
from datetime import datetime
from loguru import logger

from ...models.schemas import (
    PromptTemplate,
    PromptCreateRequest,
    PromptUpdateRequest,
    PromptListResponse,
)

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

# Prompt 模板存储目录
PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "prompts"


def _ensure_prompts_dir():
    """确保 prompts 目录存在"""
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_prompt_path(prompt_id: str) -> Path:
    """获取 prompt 文件路径"""
    return PROMPTS_DIR / f"{prompt_id}.json"


def _load_prompt(prompt_id: str) -> Optional[PromptTemplate]:
    """加载 prompt 模板"""
    path = _get_prompt_path(prompt_id)
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return PromptTemplate(**data)


def _save_prompt(prompt: PromptTemplate) -> None:
    """保存 prompt 模板"""
    path = _get_prompt_path(prompt.id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prompt.model_dump(), f, ensure_ascii=False, indent=2)


@router.get("/", response_model=PromptListResponse)
async def list_prompts(
    category: Optional[str] = Query(None, description="按分类筛选"),
    limit: int = Query(50, ge=1, le=100),
) -> PromptListResponse:
    """
    获取 Prompt 模板列表
    """
    try:
        _ensure_prompts_dir()

        prompts = []
        for file in PROMPTS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prompt = PromptTemplate(**data)

                    # 分类筛选
                    if category is None or prompt.category == category:
                        prompts.append(prompt)

            except Exception as e:
                logger.warning(f"Error loading prompt from {file}: {e}")
                continue

        # 按更新时间排序
        prompts.sort(key=lambda x: x.updated_at, reverse=True)

        # 限制数量
        prompts = prompts[:limit]

        return PromptListResponse(
            prompts=prompts,
            total=len(prompts),
        )

    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{prompt_id}", response_model=PromptTemplate)
async def get_prompt(prompt_id: str) -> PromptTemplate:
    """
    获取单个 Prompt 模板
    """
    try:
        prompt = _load_prompt(prompt_id)

        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt '{prompt_id}' not found"
            )

        return prompt

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=PromptTemplate, status_code=status.HTTP_201_CREATED)
async def create_prompt(request: PromptCreateRequest) -> PromptTemplate:
    """
    创建 Prompt 模板
    """
    try:
        _ensure_prompts_dir()

        # 生成唯一 ID
        prompt_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # 创建 prompt 模板
        prompt = PromptTemplate(
            id=prompt_id,
            name=request.name,
            content=request.content,
            category=request.category,
        )

        # 保存
        _save_prompt(prompt)

        logger.info(f"Created prompt: {prompt_id}")
        return prompt

    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{prompt_id}", response_model=PromptTemplate)
async def update_prompt(prompt_id: str, request: PromptUpdateRequest) -> PromptTemplate:
    """
    更新 Prompt 模板
    """
    try:
        # 加载现有 prompt
        prompt = _load_prompt(prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt '{prompt_id}' not found"
            )

        # 更新字段
        if request.name is not None:
            prompt.name = request.name
        if request.content is not None:
            prompt.content = request.content
        if request.category is not None:
            prompt.category = request.category

        # 更新时间戳
        prompt.updated_at = datetime.now()

        # 保存
        _save_prompt(prompt)

        logger.info(f"Updated prompt: {prompt_id}")
        return prompt

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """
    删除 Prompt 模板
    """
    try:
        path = _get_prompt_path(prompt_id)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt '{prompt_id}' not found"
            )

        # 删除文件
        path.unlink()

        logger.info(f"Deleted prompt: {prompt_id}")
        return {"success": True, "message": "Prompt deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )