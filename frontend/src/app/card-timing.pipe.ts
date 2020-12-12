import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'cardTiming'
})
export class CardTimingPipe implements PipeTransform {
  transform(values: any[]): any[] {
    let output = [];
    let alt = values.join(',').toLowerCase().split(',');
    let index = alt.indexOf('prep');
    if (index != -1) {
      let timing = values[index+1].replace('d', 'days').replace('h', 'hrs').replace('m', 'mins');
      output.push('Prep: ' + timing);
    }
    index = alt.indexOf('cook');
    if (index != -1) {
      let timing = values[index+1].replace('d', 'days').replace('h', 'hrs').replace('m', 'mins');
      output.push('Cook: ' + timing);
    }
    index = alt.indexOf('ready in');
    if (index != -1) {
      let timing = values[index+1].replace('d', 'days').replace('h', 'hrs').replace('m', 'mins');
      output.push('Total: ' + timing);
    }
    return output;
  }
}
