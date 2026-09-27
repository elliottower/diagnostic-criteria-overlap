// Text recognition with Apple's Vision framework.
// Prints one line per recognised string: text, x, y, width, height, confidence.
// Coordinates are normalised with the origin at the bottom left.
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1 else {
    FileHandle.standardError.write("usage: VisionOCR <image>\n".data(using: .utf8)!)
    exit(2)
}
guard let image = NSImage(contentsOfFile: args[1]),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot read image: \(args[1])\n".data(using: .utf8)!)
    exit(2)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false          // these are numbers, not words
request.minimumTextHeight = 0.0

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do {
    try handler.perform([request])
} catch {
    FileHandle.standardError.write("vision failed: \(error)\n".data(using: .utf8)!)
    exit(1)
}

for case let obs as VNRecognizedTextObservation in (request.results ?? []) {
    guard let best = obs.topCandidates(1).first else { continue }
    let b = obs.boundingBox
    let line = String(format: "%@\t%.6f\t%.6f\t%.6f\t%.6f\t%.3f",
                      best.string, b.origin.x, b.origin.y, b.size.width, b.size.height, best.confidence)
    print(line)
}
