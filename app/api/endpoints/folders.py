# -*- coding: utf-8 -*-
"""
@File    :   folders.py
@Time    :   2025/7/2 08:42
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from loguru import logger
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from app.curd.folders import Folders
from app.curd.chats import Chats
from app.schemas.folders import FolderModel, FolderForm, FolderParentIdForm, FolderIsExpandedForm
from app.constants import ERROR_MESSAGES

router = APIRouter()


@router.get("", response_model=list[FolderModel])
@router.get("/", response_model=list[FolderModel])
async def get_folders(user_id: str):
    """
    Retrieve all folders for the given user ID, including associated chats.

    Args:
        user_id: ID of the user whose folders are to be retrieved.

    Returns:
        List of FolderModel objects with chat titles and IDs.
    """
    folders = Folders.get_folders_by_user_id(user_id)
    return [
        {
            **folder.model_dump(),
            "items": {
                "chats": [
                    {"title": chat.title, "id": chat.id}
                    for chat in Chats.get_chats_by_folder_id_and_user_id(
                        folder.id, user_id
                    )
                ]
            },
        }
        for folder in folders
    ]


@router.post("", response_model=FolderModel)
@router.post("/", response_model=FolderModel)
async def create_folder(form_data: FolderForm, user_id: str):
    """
    Create a new folder for the given user ID.

    Args:
        form_data: Folder creation form with name.
        user_id: ID of the user creating the folder.

    Returns:
        Created FolderModel object.

    Raises:
        HTTPException: If folder already exists or creation fails.
    """
    folder = Folders.get_folder_by_parent_id_and_user_id_and_name(
        None, user_id, form_data.name
    )
    if folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Folder already exists"),
        )

    try:
        folder = Folders.insert_new_folder(user_id, form_data.name)
        if folder:
            return folder
        raise Exception("Error creating folder")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Error creating folder"),
        )


@router.get("/{id}", response_model=Optional[FolderModel])
async def get_folder_by_id(id: str, user_id: str):
    """
    Retrieve a specific folder by ID for the given user ID.

    Args:
        id: Folder ID.
        user_id: ID of the user requesting the folder.

    Returns:
        FolderModel object if found, else None.

    Raises:
        HTTPException: If folder is not found.
    """
    folder = Folders.get_folder_by_id_and_user_id(id, user_id)
    if folder:
        return folder
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ERROR_MESSAGES.NOT_FOUND,
    )


@router.post("/{id}/update", response_model=Optional[FolderModel])
async def update_folder_name_by_id(
        id: str, form_data: FolderForm, user_id: str
):
    """
    Update the name of a folder by ID for the given user ID.

    Args:
        id: Folder ID.
        form_data: Form with new folder name.
        user_id: ID of the user updating the folder.

    Returns:
        Updated FolderModel object.

    Raises:
        HTTPException: If folder not found, name already exists, or update fails.
    """
    folder = Folders.get_folder_by_id_and_user_id(id, user_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    existing_folder = Folders.get_folder_by_parent_id_and_user_id_and_name(
        folder.parent_id, user_id, form_data.name
    )
    if existing_folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Folder already exists"),
        )

    try:
        folder = Folders.update_folder_name_by_id_and_user_id(
            id, user_id, form_data.name
        )
        if folder:
            return folder
        raise Exception("Error updating folder")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Error updating folder"),
        )


@router.post("/{id}/update/parent", response_model=Optional[FolderModel])
async def update_folder_parent_id_by_id(
        id: str, form_data: FolderParentIdForm, user_id: str
):
    """
    Update the parent ID of a folder by ID for the given user ID.

    Args:
        id: Folder ID.
        form_data: Form with new parent ID.
        user_id: ID of the user updating the folder.

    Returns:
        Updated FolderModel object.

    Raises:
        HTTPException: If folder not found, name already exists, or update fails.
    """
    folder = Folders.get_folder_by_id_and_user_id(id, user_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    existing_folder = Folders.get_folder_by_parent_id_and_user_id_and_name(
        form_data.parent_id, user_id, folder.name
    )
    if existing_folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Folder already exists"),
        )

    try:
        folder = Folders.update_folder_parent_id_by_id_and_user_id(
            id, user_id, form_data.parent_id
        )
        if folder:
            return folder
        raise Exception("Error updating folder")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Error updating folder"),
        )


@router.post("/{id}/update/expanded", response_model=Optional[FolderModel])
async def update_folder_is_expanded_by_id(
        id: str, form_data: FolderIsExpandedForm, user_id: str
):
    """
    Update the expanded status of a folder by ID for the given user ID.

    Args:
        id: Folder ID.
        form_data: Form with expanded status.
        user_id: ID of the user updating the folder.

    Returns:
        Updated FolderModel object.

    Raises:
        HTTPException: If folder not found or update fails.
    """
    folder = Folders.get_folder_by_id_and_user_id(id, user_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    try:
        folder = Folders.update_folder_is_expanded_by_id_and_user_id(
            id, user_id, form_data.is_expanded
        )
        if folder:
            return folder
        raise Exception("Error updating folder")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Error updating folder"),
        )


@router.delete("/{id}", response_model=bool)
async def delete_folder_by_id(id: str, user_id: str):
    """
    Delete a folder by ID for the given user ID, including all subfolders and chats.

    Args:
        id: Folder ID.
        user_id: ID of the user deleting the folder.

    Returns:
        True if deletion is successful.

    Raises:
        HTTPException: If folder not found or deletion fails.
    """
    folder = Folders.get_folder_by_id_and_user_id(id, user_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    try:
        result = Folders.delete_folder_by_id_and_user_id(id, user_id)
        if result:
            return result
        raise Exception("Error deleting folder")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Error deleting folder"),
        )