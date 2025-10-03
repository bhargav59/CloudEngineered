"""
Unit tests for Tool models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tools.models import Tool, Category, ToolReview, ToolComparison
from decimal import Decimal

User = get_user_model()


class CategoryModelTests(TestCase):
    """Test cases for Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="CI/CD Tools",
            description="Continuous Integration and Continuous Deployment tools",
            icon="fas fa-cog",
            color="#3B82F6",
            is_featured=True,
            sort_order=1
        )
    
    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.name, "CI/CD Tools")
        self.assertEqual(self.category.slug, "cicd-tools")
        self.assertTrue(self.category.is_featured)
    
    def test_category_string_representation(self):
        """Test category __str__ method"""
        self.assertEqual(str(self.category), "CI/CD Tools")
    
    def test_category_slug_generation(self):
        """Test slug is automatically generated from name"""
        category = Category.objects.create(
            name="Test Category",
            description="Test description"
        )
        self.assertEqual(category.slug, "test-category")
    
    def test_category_tool_count(self):
        """Test tool_count property"""
        user = User.objects.create_user(username='testuser', password='testpass123')
        Tool.objects.create(
            name="Test Tool",
            description="Test description",
            category=self.category,
            website_url="https://example.com",
            pricing_model="free",
            is_published=True,
        )
        self.assertEqual(self.category.tool_count, 1)


class ToolModelTests(TestCase):
    """Test cases for Tool model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.category = Category.objects.create(
            name="Containers",
            description="Container tools",
        )
        self.tool = Tool.objects.create(
            name="Docker",
            description="Container platform for building and running applications",
            tagline="Build, Ship, and Run Anywhere",
            category=self.category,
            website_url="https://docker.com",
            github_url="https://github.com/docker/docker",
            pricing_model="freemium",
            is_published=True,
            is_featured=True,
        )
    
    def test_tool_creation(self):
        """Test tool is created correctly"""
        self.assertEqual(self.tool.name, "Docker")
        self.assertEqual(self.tool.slug, "docker")
        self.assertTrue(self.tool.is_published)
        self.assertTrue(self.tool.is_featured)
    
    def test_tool_string_representation(self):
        """Test tool __str__ method"""
        self.assertEqual(str(self.tool), "Docker")
    
    def test_tool_slug_generation(self):
        """Test slug is automatically generated from name"""
        self.assertEqual(self.tool.slug, "docker")
    
    def test_tool_rating_property(self):
        """Test rating property calculation"""
        # Initially no ratings
        self.assertEqual(self.tool.rating, 0.0)
        
        # Add rating data
        self.tool.rating_sum = 45
        self.tool.rating_count = 10
        self.tool.save()
        self.assertEqual(self.tool.rating, 4.5)
    
    def test_tool_github_repo_name(self):
        """Test GitHub repo name extraction"""
        self.assertEqual(self.tool.github_repo_name, "docker/docker")
    
    def test_tool_add_tag(self):
        """Test adding tags to tool"""
        self.tool.add_tag("containerization")
        self.assertIn("containerization", self.tool.tags)
    
    def test_tool_remove_tag(self):
        """Test removing tags from tool"""
        self.tool.tags = ["docker", "containers"]
        self.tool.save()
        self.tool.remove_tag("docker")
        self.assertNotIn("docker", self.tool.tags)
        self.assertIn("containers", self.tool.tags)
    
    def test_tool_view_count_increment(self):
        """Test view count increments correctly"""
        initial_count = self.tool.view_count
        self.tool.view_count += 1
        self.tool.save()
        self.tool.refresh_from_db()
        self.assertEqual(self.tool.view_count, initial_count + 1)
    
    def test_tool_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.tool.get_absolute_url()
        self.assertIn(self.category.slug, url)
        self.assertIn(self.tool.slug, url)


class ToolReviewModelTests(TestCase):
    """Test cases for ToolReview model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            password='testpass123',
            email='reviewer@example.com'
        )
        self.category = Category.objects.create(
            name="Testing",
            description="Testing tools"
        )
        self.tool = Tool.objects.create(
            name="Jest",
            description="JavaScript testing framework",
            category=self.category,
            website_url="https://jestjs.io",
            pricing_model="free",
            is_published=True,
        )
        self.review = ToolReview.objects.create(
            tool=self.tool,
            user=self.user,
            title="Excellent Testing Framework",
            content="Jest makes testing JavaScript applications easy and enjoyable.",
            rating=5,
            usage_duration="1-2 years",
            is_verified=True
        )
    
    def test_review_creation(self):
        """Test review is created correctly"""
        self.assertEqual(self.review.title, "Excellent Testing Framework")
        self.assertEqual(self.review.rating, 5)
        self.assertTrue(self.review.is_verified)
    
    def test_review_string_representation(self):
        """Test review __str__ method"""
        self.assertIn("Jest", str(self.review))
        self.assertIn("reviewer", str(self.review))
    
    def test_review_rating_range(self):
        """Test review rating is within valid range"""
        self.assertGreaterEqual(self.review.rating, 1)
        self.assertLessEqual(self.review.rating, 5)
    
    def test_helpful_count_increment(self):
        """Test helpful count can be incremented"""
        self.review.helpful_count = 10
        self.review.save()
        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 10)


class ToolComparisonModelTests(TestCase):
    """Test cases for ToolComparison model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='comparer',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="Containers",
            description="Container tools"
        )
        self.tool1 = Tool.objects.create(
            name="Docker",
            description="Container platform",
            category=self.category,
            website_url="https://docker.com",
            pricing_model="freemium",
            is_published=True,
        )
        self.tool2 = Tool.objects.create(
            name="Podman",
            description="Daemonless container engine",
            category=self.category,
            website_url="https://podman.io",
            pricing_model="free",
            is_published=True,
        )
        self.comparison = ToolComparison.objects.create(
            title="Docker vs Podman: Container Showdown",
            description="Comparing two popular container engines",
            is_published=True
        )
        self.comparison.tools.add(self.tool1, self.tool2)
    
    def test_comparison_creation(self):
        """Test comparison is created correctly"""
        self.assertEqual(self.comparison.title, "Docker vs Podman: Container Showdown")
        self.assertTrue(self.comparison.is_published)
    
    def test_comparison_tools_count(self):
        """Test comparison has correct number of tools"""
        self.assertEqual(self.comparison.tools.count(), 2)
    
    def test_comparison_slug_generation(self):
        """Test slug is generated from title"""
        self.assertEqual(self.comparison.slug, "docker-vs-podman-container-showdown")
    
    def test_comparison_string_representation(self):
        """Test comparison __str__ method"""
        self.assertIn("Docker", str(self.comparison))


class ToolModelMethodsTests(TestCase):
    """Test specific methods and properties of Tool model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.category = Category.objects.create(name="Test Category", description="Test")
        self.tool = Tool.objects.create(
            name="Test Tool",
            description="Test description",
            category=self.category,
            website_url="https://example.com",
            github_url="https://github.com/owner/repo",
            pricing_model="free",
        )
    
    def test_github_repo_name_with_valid_url(self):
        """Test GitHub repo name extraction with valid URL"""
        self.assertEqual(self.tool.github_repo_name, "owner/repo")
    
    def test_github_repo_name_with_trailing_slash(self):
        """Test GitHub repo name extraction with trailing slash"""
        self.tool.github_url = "https://github.com/owner/repo/"
        self.assertEqual(self.tool.github_repo_name, "owner/repo")
    
    def test_github_repo_name_without_url(self):
        """Test GitHub repo name when no URL is set"""
        self.tool.github_url = ""
        self.assertIsNone(self.tool.github_repo_name)
    
    def test_rating_with_no_ratings(self):
        """Test rating calculation with zero ratings"""
        self.tool.rating_count = 0
        self.tool.rating_sum = 0
        self.assertEqual(self.tool.rating, 0.0)
    
    def test_rating_with_multiple_ratings(self):
        """Test rating calculation with multiple ratings"""
        self.tool.rating_sum = 42
        self.tool.rating_count = 10
        self.tool.save()
        self.assertEqual(self.tool.rating, 4.2)
    
    def test_rating_rounding(self):
        """Test rating is rounded to 1 decimal place"""
        self.tool.rating_sum = 44
        self.tool.rating_count = 10
        self.tool.save()
        self.assertEqual(self.tool.rating, 4.4)
