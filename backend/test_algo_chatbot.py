#!/usr/bin/env python3
"""
Test script for Algorithmic Trading and AI Chatbot services
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

async def test_algo_trading():
    """Test the algorithmic trading service"""
    print("🧪 Testing Algorithmic Trading Service...")
    
    try:
        from services.algo_trading import (
            algo_trading_service, StrategyConfig, StrategyType
        )
        
        # Test creating a strategy
        config = StrategyConfig(
            strategy_id="test_strategy_001",
            name="Test Moving Average Strategy",
            strategy_type=StrategyType.MOVING_AVERAGE_CROSSOVER,
            symbols=["AAPL", "GOOGL"],
            parameters={"short_ma": 10, "long_ma": 20},
            risk_limits={
                "max_position_risk": 0.02,
                "max_position_size": 1000,
                "max_risk_per_trade": 1000
            }
        )
        
        # Add strategy
        success = await algo_trading_service.add_strategy(config)
        print(f"✅ Strategy creation: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            # Get strategy status
            status = await algo_trading_service.get_strategy_status("test_strategy_001")
            print(f"✅ Strategy status: {status}")
            
            # Start strategy
            start_success = await algo_trading_service.start_strategy("test_strategy_001")
            print(f"✅ Strategy start: {'SUCCESS' if start_success else 'FAILED'}")
            
            # Get all strategies
            all_strategies = await algo_trading_service.get_all_strategies()
            print(f"✅ Total strategies: {len(all_strategies)}")
            
            # Clean up
            await algo_trading_service.remove_strategy("test_strategy_001")
            print("✅ Strategy cleanup: SUCCESS")
        
    except Exception as e:
        print(f"❌ Algo trading test failed: {e}")
        return False
    
    return True

async def test_ai_chatbot():
    """Test the AI chatbot service"""
    print("\n🤖 Testing AI Chatbot Service...")
    
    try:
        from services.ai_chatbot import ai_chatbot
        
        # Test processing a message
        response = await ai_chatbot.process_message("user123", "Hello! What can you help me with?")
        print(f"✅ Chatbot response: {response.intent.value}")
        print(f"✅ Response content length: {len(response.content)}")
        print(f"✅ Suggested actions: {len(response.suggested_actions)}")
        
        # Test market analysis
        market_response = await ai_chatbot.process_message("user123", "What's the current market outlook?")
        print(f"✅ Market analysis intent: {market_response.intent.value}")
        
        # Test strategy recommendation
        strategy_response = await ai_chatbot.process_message("user123", "Recommend a trading strategy")
        print(f"✅ Strategy recommendation intent: {strategy_response.intent.value}")
        
        # Test conversation history
        history = ai_chatbot.get_conversation_history("user123", 5)
        print(f"✅ Conversation history: {len(history)} messages")
        
    except Exception as e:
        print(f"❌ AI chatbot test failed: {e}")
        return False
    
    return True

async def test_services_integration():
    """Test integration between services"""
    print("\n🔗 Testing Services Integration...")
    
    try:
        # Test that both services can work together
        from services.algo_trading import algo_trading_service
        from services.ai_chatbot import ai_chatbot
        
        # Create a strategy and ask chatbot about it
        config = StrategyConfig(
            strategy_id="integration_test_001",
            name="Integration Test Strategy",
            strategy_type=StrategyType.MEAN_REVERSION,
            symbols=["TSLA"],
            parameters={"lookback": 15, "std_threshold": 1.5},
            risk_limits={"max_position_risk": 0.015, "max_position_size": 500}
        )
        
        await algo_trading_service.add_strategy(config)
        
        # Ask chatbot about mean reversion strategy
        response = await ai_chatbot.process_message("user123", "Tell me about mean reversion strategy")
        print(f"✅ Integration test response: {response.intent.value}")
        
        # Clean up
        await algo_trading_service.remove_strategy("integration_test_001")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Algorithmic Trading and AI Chatbot Tests...\n")
    
    tests = [
        ("Algorithmic Trading", test_algo_trading),
        ("AI Chatbot", test_ai_chatbot),
        ("Services Integration", test_services_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Services are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
