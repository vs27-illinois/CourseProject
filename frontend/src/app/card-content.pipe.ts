import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'cardContent'
})
export class CardContentPipe implements PipeTransform {
  transform(value: string): string {
    return '<u>Ingredients:</u> ' + value;
  }
}
