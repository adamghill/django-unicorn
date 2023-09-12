import morphdom from "./morphdom/2.6.1/morphdom.js";
import {getMorphdomOptions} from "./morphdom/2.6.1/options.js";


export function getMorphFn(morpherName) {
  if (morpherName === "morphdom") {
    return morphdomMorph;
  }
  if (morpherName === "alpine") {
    if (typeof Alpine === "undefined" || !Alpine.morph) {
      throw Error(`
Alpine morpher requires Alpine to be loaded. Add Alpine and Alpine Morph to your page. E.g., add the following to your base.html:

  <script defer src="https://unpkg.com/@alpinejs/morph@3.x.x/dist/cdn.min.js"></script>
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
`);
    }
    return alpineMorph;
  }
  throw Error(`No morpher found for: ${morpherName}`);
}


function morphdomMorph(el, newHtml, reloadScriptElements) {
  morphdom(el, newHtml, getMorphdomOptions(reloadScriptElements));
}

function alpineMorph(el, newHtml) {
  return Alpine.morph(el, newHtml);
}
