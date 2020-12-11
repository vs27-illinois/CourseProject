import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class RecipeService {

  constructor(
    private http: HttpClient
  ) {}

  getRecipes(ingredient) {
    return this.http.get<any[]>('/recipe/search/' + ingredient);
  }

  getRecipeDetails(recipeId) {
    return this.http.get<any[]>('/recipe/details/' + recipeId);
  }

  getRecommendedRecipes(recipeId) {
    return this.http.get<any[]>('/recipe/recommend/' + recipeId);
  }

}
