"""
Tests for Command Interceptor
"""
import pytest
import asyncio
from core.interceptor import CommandInterceptor
from data.models import RiskLevel

interceptor = CommandInterceptor()

@pytest.mark.asyncio
async def test_safe_passthrough():
    result = await interceptor.intercept("ls -la")
    assert result.should_block == False
    assert result.risk_level == RiskLevel.SAFE

@pytest.mark.asyncio
async def test_empty_command():
    result = await interceptor.intercept("")
    assert result.should_block == False

@pytest.mark.asyncio
async def test_hard_block():
    result = await interceptor.intercept("rm -rf /")
    assert result.should_block == True
    assert result.is_hard_block == True
    assert result.risk_level == RiskLevel.CRITICAL
