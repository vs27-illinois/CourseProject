import { Component } from '@angular/core';
import { RecipeService } from './recipe.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  showDetails = false;
  title = 'RecipeFinder';
  message = 'Welcome to RecipeFinder! Please search with an ingredient name to start...';
  buttonText = "Close";
  details = {};
  recipes = [];
  recommends = [];
  pageStack = [];

  constructor(
    private recipeService: RecipeService
  ) {}

  onInputSubmit(query) {
    let ingredient = query.replace(/[^a-zA-Z0-9 ]/g, '').trim();
    if (ingredient.length > 0) {
      this.recipeService.getRecipes(ingredient)
          .subscribe(data => {
            this.recipes = data;
            this.showDetails = false;
            this.message = 'No recipes to show!';
            this.buttonText = "Close";
            this.details = {};
            this.recommends = [];
            this.pageStack = [];
          });
    } else {
      this.recipes = [];
      this.showDetails = false;
      this.message = 'No recipes to show!';
      this.buttonText = "Close";
      this.details = {};
      this.recommends = [];
      this.pageStack = [];
    }
  }

  onCardClick(recipeId) {
    this.recipeService.getRecipeDetails(recipeId)
        .subscribe(data => {
          this.details = data;
          window.scrollTo(0, 0);
          this.showDetails = true;
          this.pageStack.push(recipeId);
          if (this.pageStack.length > 1) {
            this.buttonText = "Back";
          } else {
            this.buttonText = "Close";
          }
        });
    this.recipeService.getRecommendedRecipes(recipeId)
        .subscribe(data => this.recommends = data);
  }

  onTitleClick() {
    this.showDetails = false;
    this.buttonText = "Close";
    this.details = {};
    this.recommends = [];
    this.pageStack = [];
  }

  onCloseClick() {
    this.pageStack.pop();
    if (this.pageStack.length < 1) {
      this.onTitleClick();
    } else {
      let recipeId = this.pageStack.pop();
      this.onCardClick(recipeId);
    }
  }
}
