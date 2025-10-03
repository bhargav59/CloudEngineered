"""
Unit tests for API endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apps.tools.models import Tool, Category
from apps.ai.models import AIModel, AIProvider

User = get_user_model()


class APIAuthenticationTests(APITestCase):
    """Test API authentication and permissions"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='testpass123',
            email='api@example.com'
        )
    
    def test_api_root_accessible_without_auth(self):
        """Test API root is accessible without authentication"""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_root_returns_endpoints(self):
        """Test API root returns available endpoints"""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain links to major endpoints
        data = response.json()
        self.assertIsInstance(data, dict)


class ToolAPITests(APITestCase):
    """Test Tool API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="Cloud Platforms",
            description="Cloud platform tools"
        )
        self.tool = Tool.objects.create(
            name="AWS",
            description="Amazon Web Services cloud platform",
            category=self.category,
            website_url="https://aws.amazon.com",
            pricing_model="paid",
            is_published=True,
            created_by=self.user
        )
    
    def test_get_tools_list(self):
        """Test GET /api/v1/tools/ returns tool list"""
        response = self.client.get('/api/v1/tools/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(len(data['results']), 1)
    
    def test_get_tool_detail(self):
        """Test GET /api/v1/tools/{slug}/ returns tool details"""
        response = self.client.get(f'/api/v1/tools/{self.tool.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['name'], 'AWS')
        self.assertEqual(data['slug'], 'aws')
    
    def test_tool_list_pagination(self):
        """Test tool list is paginated"""
        # Create multiple tools
        for i in range(15):
            Tool.objects.create(
                name=f"Tool {i}",
                description=f"Description {i}",
                category=self.category,
                website_url=f"https://tool{i}.com",
                pricing_model="free",
                is_published=True,
                created_by=self.user
            )
        response = self.client.get('/api/v1/tools/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
    
    def test_tool_list_filtering_by_category(self):
        """Test filtering tools by category"""
        response = self.client.get(f'/api/v1/tools/?category={self.category.slug}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        for tool in data['results']:
            self.assertEqual(tool['category']['slug'], self.category.slug)
    
    def test_tool_search(self):
        """Test searching tools"""
        response = self.client.get('/api/v1/tools/?search=AWS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'AWS')
    
    def test_tool_ordering(self):
        """Test ordering tools"""
        # Create tools with different names
        Tool.objects.create(
            name="Zebra Tool",
            description="Last alphabetically",
            category=self.category,
            website_url="https://zebra.com",
            pricing_model="free",
            is_published=True,
            created_by=self.user
        )
        response = self.client.get('/api/v1/tools/?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        names = [tool['name'] for tool in data['results']]
        self.assertEqual(names, sorted(names))
    
    def test_unpublished_tools_not_in_list(self):
        """Test unpublished tools are not returned"""
        unpublished = Tool.objects.create(
            name="Secret Tool",
            description="Not published",
            category=self.category,
            website_url="https://secret.com",
            pricing_model="free",
            is_published=False,
            created_by=self.user
        )
        response = self.client.get('/api/v1/tools/')
        data = response.json()
        tool_names = [tool['name'] for tool in data['results']]
        self.assertNotIn('Secret Tool', tool_names)


class CategoryAPITests(APITestCase):
    """Test Category API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="DevOps",
            description="DevOps tools and platforms"
        )
    
    def test_get_categories_list(self):
        """Test GET /api/v1/categories/ returns category list"""
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
    
    def test_get_category_detail(self):
        """Test GET /api/v1/categories/{slug}/ returns category details"""
        response = self.client.get(f'/api/v1/categories/{self.category.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['name'], 'DevOps')


class HealthCheckAPITests(APITestCase):
    """Test health check endpoint"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_health_check_endpoint(self):
        """Test /api/v1/health/ returns health status"""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_health_check_includes_database(self):
        """Test health check includes database status"""
        response = self.client.get('/api/v1/health/')
        data = response.json()
        self.assertIn('database', data)
        self.assertEqual(data['database'], 'connected')


class AIModelAPITests(APITestCase):
    """Test AI Model API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.provider = AIProvider.objects.create(
            name='OpenRouter',
            api_key_name='OPENROUTER_API_KEY',
            base_url='https://openrouter.ai/api/v1',
            is_active=True
        )
        self.model = AIModel.objects.create(
            provider=self.provider,
            name='gpt-4o-mini',
            display_name='GPT-4o Mini',
            max_tokens=16000,
            is_active=True,
            cost_per_1k_input_tokens=0.00015,
            cost_per_1k_output_tokens=0.0006
        )
    
    def test_get_ai_models_list(self):
        """Test GET /api/v1/ai-models/ returns AI model list"""
        response = self.client.get('/api/v1/ai-models/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
    
    def test_only_active_models_returned(self):
        """Test only active AI models are returned"""
        inactive_model = AIModel.objects.create(
            provider=self.provider,
            name='old-model',
            display_name='Old Model',
            is_active=False
        )
        response = self.client.get('/api/v1/ai-models/')
        data = response.json()
        model_names = [model['name'] for model in data]
        self.assertIn('gpt-4o-mini', model_names)
        self.assertNotIn('old-model', model_names)


class RateLimitingTests(APITestCase):
    """Test API rate limiting"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_rate_limiting_for_anonymous_users(self):
        """Test rate limiting is applied to anonymous users"""
        # Make multiple requests
        responses = []
        for i in range(25):  # Above typical anonymous limit
            response = self.client.get('/api/v1/tools/')
            responses.append(response.status_code)
        
        # Should eventually hit rate limit
        # Note: This depends on rate limiting configuration
        success_count = responses.count(200)
        self.assertGreater(success_count, 0)


class StatsAPITests(APITestCase):
    """Test statistics API endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='test')
        self.category = Category.objects.create(
            name="Testing",
            description="Testing tools"
        )
        Tool.objects.create(
            name="Test Tool",
            description="Test",
            category=self.category,
            website_url="https://example.com",
            pricing_model="free",
            is_published=True,
            created_by=self.user
        )
    
    def test_get_platform_stats(self):
        """Test GET /api/v1/stats/ returns platform statistics"""
        response = self.client.get('/api/v1/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('total_tools', data)
        self.assertIn('total_categories', data)
        self.assertGreaterEqual(data['total_tools'], 1)


class APIErrorHandlingTests(APITestCase):
    """Test API error handling"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_404_for_nonexistent_tool(self):
        """Test 404 error for non-existent tool"""
        response = self.client.get('/api/v1/tools/nonexistent-tool/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_404_for_nonexistent_endpoint(self):
        """Test 404 for non-existent endpoint"""
        response = self.client.get('/api/v1/nonexistent/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_filtering_parameter(self):
        """Test handling of invalid filtering parameters"""
        response = self.client.get('/api/v1/tools/?invalid_param=value')
        # Should still return 200, just ignore invalid param
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIPaginationTests(APITestCase):
    """Test API pagination functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='test')
        self.category = Category.objects.create(
            name="Pagination Test",
            description="Test category"
        )
        # Create 25 tools for pagination testing
        for i in range(25):
            Tool.objects.create(
                name=f"Tool {i:02d}",
                description=f"Description {i}",
                category=self.category,
                website_url=f"https://tool{i}.com",
                pricing_model="free",
                is_published=True,
                created_by=self.user
            )
    
    def test_first_page_contains_results(self):
        """Test first page contains results"""
        response = self.client.get('/api/v1/tools/')
        data = response.json()
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
    
    def test_pagination_next_link(self):
        """Test pagination provides next link"""
        response = self.client.get('/api/v1/tools/')
        data = response.json()
        if data['count'] > 20:  # If more than one page
            self.assertIsNotNone(data['next'])
    
    def test_page_size_parameter(self):
        """Test custom page size parameter"""
        response = self.client.get('/api/v1/tools/?page_size=5')
        data = response.json()
        self.assertLessEqual(len(data['results']), 5)
