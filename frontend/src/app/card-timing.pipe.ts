import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'cardTiming'
})
export class CardTimingPipe implements PipeTransform {
  transform(values: any[]): any[] {
    let output = [];
    let alt = values.join(',').toLowerCase().split(',');
    let map = {
      'prep': 'Prep',
      'cook': 'Cook',
      'ready in': 'Total'
    };
    Object.keys(map).map(key => {
      let index = alt.indexOf(key);
      if (index != -1) {
        let timing = values[index+1].replace('d', 'days').replace('h', 'hrs').replace('m', 'mins');
        output.push(map[key] + ': ' + timing);
      }
    });
    return output;
  }
}
