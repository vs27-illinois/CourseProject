import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'cardTooltip'
})
export class CardTooltipPipe implements PipeTransform {
  transform(value: string): string {
    return value.replace(/<\/?strong>/gi, '');
  }
}
