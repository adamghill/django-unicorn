import { MorphdomMorpher } from "./morphers/morphdom.js";
import { AlpineMorpher } from "./morphers/alpine.js";

export function getMorpher(morpherName, morpherOptions) {
  const MorpherClass = {
    morphdom: MorphdomMorpher,
    alpine: AlpineMorpher,
  }[morpherName];
  if (MorpherClass) {
    return new MorpherClass(morpherOptions);
  }
  throw Error(`No morpher found for: ${morpherName}`);
}
