"""
Enhanced Comparison Engine
Provides visual feature matrix and advanced comparison capabilities.
"""
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.tools.models import Tool, ToolComparison
from typing import List, Dict, Any
import json


class ComparisonMatrix(models.Model):
    """
    Feature comparison matrix for tools.
    Supports visual comparison with scores and badges.
    """
    comparison = models.OneToOneField(
        ToolComparison,
        on_delete=models.CASCADE,
        related_name='matrix'
    )
    
    # Feature categories
    categories = models.JSONField(
        default=list,
        help_text="List of feature categories: ['Performance', 'Security', 'Pricing', etc.]"
    )
    
    # Feature matrix data
    # Structure: {category: {feature: {tool_id: {value, score, badge}}}}
    matrix_data = models.JSONField(
        default=dict,
        help_text="Complete feature comparison matrix"
    )
    
    # Visual settings
    highlight_differences = models.BooleanField(default=True)
    show_scores = models.BooleanField(default=True)
    show_badges = models.BooleanField(default=True)
    
    # Scoring weights
    category_weights = models.JSONField(
        default=dict,
        help_text="Weight for each category in overall score calculation"
    )
    
    # Overall scores
    tool_scores = models.JSONField(
        default=dict,
        help_text="Overall scores for each tool: {tool_id: score}"
    )
    
    # Winner analysis
    winner_by_category = models.JSONField(
        default=dict,
        help_text="Best tool for each category"
    )
    overall_winner = models.ForeignKey(
        Tool,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comparison_wins'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Comparison Matrix'
        verbose_name_plural = 'Comparison Matrices'
    
    def __str__(self):
        return f"Matrix for {self.comparison.title}"
    
    def calculate_scores(self):
        """Calculate scores for all tools in the comparison."""
        tool_scores = {}
        category_winners = {}
        
        for category, features in self.matrix_data.items():
            category_weight = self.category_weights.get(category, 1.0)
            category_scores = {}
            
            for feature, tool_data in features.items():
                for tool_id, data in tool_data.items():
                    score = data.get('score', 0)
                    if tool_id not in tool_scores:
                        tool_scores[tool_id] = 0
                    if tool_id not in category_scores:
                        category_scores[tool_id] = 0
                    
                    tool_scores[tool_id] += score * category_weight
                    category_scores[tool_id] += score
            
            # Find category winner
            if category_scores:
                winner_id = max(category_scores.items(), key=lambda x: x[1])[0]
                category_winners[category] = winner_id
        
        # Normalize scores to 0-100
        if tool_scores:
            max_score = max(tool_scores.values())
            if max_score > 0:
                tool_scores = {k: round((v / max_score) * 100, 1) for k, v in tool_scores.items()}
        
        self.tool_scores = tool_scores
        self.winner_by_category = category_winners
        
        # Determine overall winner
        if tool_scores:
            winner_id = max(tool_scores.items(), key=lambda x: x[1])[0]
            try:
                self.overall_winner = Tool.objects.get(id=winner_id)
            except Tool.DoesNotExist:
                pass
        
        self.save()
        return tool_scores


class ComparisonFeature(models.Model):
    """
    Individual feature for comparison.
    Defines what to compare and how to score it.
    """
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Scoring
    weight = models.FloatField(default=1.0)
    scoring_type = models.CharField(
        max_length=20,
        choices=[
            ('boolean', 'Yes/No'),
            ('numeric', 'Numeric Value'),
            ('scale', '1-5 Scale'),
            ('percentage', 'Percentage'),
            ('custom', 'Custom'),
        ],
        default='boolean'
    )
    
    # Display
    icon = models.CharField(max_length=50, blank=True)
    badge_success = models.CharField(max_length=50, default='✓')
    badge_failure = models.CharField(max_length=50, default='✗')
    
    # Metadata
    is_critical = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'display_order', 'name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category}: {self.name}"


class ComparisonPreset(models.Model):
    """
    Pre-configured comparison templates for common scenarios.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Applicable categories
    tool_categories = models.JSONField(
        default=list,
        help_text="Tool categories this preset applies to"
    )
    
    # Features to include
    features = models.ManyToManyField(ComparisonFeature)
    
    # Category weights
    category_weights = models.JSONField(default=dict)
    
    # Visual settings
    layout = models.CharField(
        max_length=20,
        choices=[
            ('table', 'Table View'),
            ('cards', 'Card View'),
            ('side_by_side', 'Side by Side'),
        ],
        default='table'
    )
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name


class ComparisonService:
    """
    Service for creating and managing comparisons.
    """
    
    @staticmethod
    def create_comparison_matrix(comparison: ToolComparison, preset: ComparisonPreset = None) -> ComparisonMatrix:
        """
        Create a comparison matrix from a ToolComparison.
        
        Args:
            comparison: ToolComparison instance
            preset: Optional ComparisonPreset to use
        
        Returns:
            ComparisonMatrix instance
        """
        tools = comparison.tools.all()
        
        if preset:
            features = preset.features.filter(is_active=True)
            category_weights = preset.category_weights
        else:
            features = ComparisonFeature.objects.filter(is_active=True)
            category_weights = {}
        
        # Build matrix data structure
        matrix_data = {}
        categories = set()
        
        for feature in features:
            categories.add(feature.category)
            
            if feature.category not in matrix_data:
                matrix_data[feature.category] = {}
            
            matrix_data[feature.category][feature.name] = {}
            
            for tool in tools:
                # Extract feature value from tool
                value = ComparisonService._extract_feature_value(tool, feature)
                score = ComparisonService._calculate_feature_score(value, feature)
                badge = ComparisonService._get_feature_badge(value, feature)
                
                matrix_data[feature.category][feature.name][str(tool.id)] = {
                    'value': value,
                    'score': score,
                    'badge': badge,
                    'tool_name': tool.name
                }
        
        # Create or update matrix
        matrix, created = ComparisonMatrix.objects.get_or_create(
            comparison=comparison,
            defaults={
                'categories': list(categories),
                'matrix_data': matrix_data,
                'category_weights': category_weights
            }
        )
        
        if not created:
            matrix.categories = list(categories)
            matrix.matrix_data = matrix_data
            matrix.category_weights = category_weights
            matrix.save()
        
        # Calculate scores
        matrix.calculate_scores()
        
        return matrix
    
    @staticmethod
    def _extract_feature_value(tool: Tool, feature: ComparisonFeature) -> Any:
        """Extract feature value from tool model."""
        feature_map = {
            'GitHub Stars': tool.github_stars,
            'GitHub Forks': tool.github_forks,
            'Contributors': tool.github_contributors,
            'Open Issues': tool.github_open_issues,
            'Last Updated': tool.github_updated_at,
            'Performance Score': tool.performance_score,
            'Free Tier': tool.free_tier_available,
            'API Available': tool.api_available,
            'Documentation Quality': tool.documentation_quality,
            'Community Size': tool.community_size,
        }
        
        return feature_map.get(feature.name, 'N/A')
    
    @staticmethod
    def _calculate_feature_score(value: Any, feature: ComparisonFeature) -> float:
        """Calculate score for a feature value."""
        if value == 'N/A' or value is None:
            return 0.0
        
        if feature.scoring_type == 'boolean':
            return 10.0 if value else 0.0
        
        elif feature.scoring_type == 'numeric':
            # Normalize to 0-10 scale (example logic)
            if isinstance(value, (int, float)):
                return min(value / 1000, 10.0)  # Example normalization
            return 0.0
        
        elif feature.scoring_type == 'scale':
            if isinstance(value, (int, float)):
                return value * 2  # Convert 1-5 to 2-10
            return 0.0
        
        elif feature.scoring_type == 'percentage':
            if isinstance(value, (int, float)):
                return value / 10  # Convert 0-100 to 0-10
            return 0.0
        
        return 5.0  # Default middle score
    
    @staticmethod
    def _get_feature_badge(value: Any, feature: ComparisonFeature) -> str:
        """Get display badge for feature value."""
        if value == 'N/A' or value is None:
            return '−'
        
        if feature.scoring_type == 'boolean':
            return feature.badge_success if value else feature.badge_failure
        
        return str(value)
