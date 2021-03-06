import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { HttpClientModule } from '@angular/common/http';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatCardModule } from '@angular/material/card';
import { MatRippleModule } from '@angular/material/core';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { CardTooltipPipe } from './card-tooltip.pipe';
import { CardContentPipe } from './card-content.pipe';
import { CardTimingPipe } from './card-timing.pipe';

@NgModule({
  declarations: [
    AppComponent,
    CardTooltipPipe,
    CardContentPipe,
    CardTimingPipe
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatGridListModule,
    MatCardModule,
    MatRippleModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    NgbModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
