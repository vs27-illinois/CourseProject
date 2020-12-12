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
  showDetails = false;

  constructor(
    private recipeService: RecipeService
  ) {}

  onSubmit(query) {
    let ingredient = query.trim();
    if (ingredient.length > 0) {
      this.recipeService.getRecipes(ingredient)
          .subscribe(data => {
            this.recipes = data;
            this.showDetails = false;
          });
    }
  }

  onClick(recipeId) {
    this.recipeService.getRecipeDetails(recipeId)
        .subscribe(data => {
          this.details = data;
          this.showDetails = true;
        });
    this.recipeService.getRecommendedRecipes(recipeId)
        .subscribe(data => this.recommend = data);
  }

  closeDetails() {
    this.showDetails = false;
  }
}
