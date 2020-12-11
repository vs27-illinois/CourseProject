import { Component } from '@angular/core';
import { RecipeService } from './recipe.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'RecipeFinder';
  recipes = [];
  details = {};
  recommend = [];

  constructor(
    private recipeService: RecipeService
  ) {}

  onSubmit(query) {
    let ingredient = query.trim();
    if (ingredient.length > 0) {
      this.recipeService.getRecipes(ingredient)
          .subscribe(data => this.recipes = data);
    }
  }

  onClick(recipeId) {
    this.recipeService.getRecipeDetails(recipeId)
        .subscribe(data => this.details = data);
    this.recipeService.getRecommendedRecipes(recipeId)
        .subscribe(data => this.recommend = data);
  }
}
