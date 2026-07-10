import { assertEquals } from "@std/assert";
import { applyFilters, facetCounts, serviceOf } from "./filter.js";

const ARNS = [
  "arn:aws:s3:::my-bucket",
  "arn:aws:s3:::other-bucket",
  "arn:aws:lambda:us-east-1:123:function:handler",
];

Deno.test("serviceOf extracts the service segment", () => {
  assertEquals(serviceOf("arn:aws:s3:::my-bucket"), "s3");
  assertEquals(serviceOf("not-an-arn"), "");
});

Deno.test("facetCounts counts per service, sorted by name", () => {
  assertEquals(facetCounts(ARNS), [["lambda", 1], ["s3", 2]]);
});

Deno.test("applyFilters: empty text and no facets returns everything", () => {
  assertEquals(applyFilters(ARNS, "", new Set()), ARNS);
});

Deno.test("applyFilters: text is case-insensitive substring", () => {
  assertEquals(applyFilters(ARNS, "MY-BUCKET", new Set()), ["arn:aws:s3:::my-bucket"]);
});

Deno.test("applyFilters: facets OR together and AND with text", () => {
  assertEquals(applyFilters(ARNS, "", new Set(["s3"])).length, 2);
  assertEquals(applyFilters(ARNS, "other", new Set(["s3"])), ["arn:aws:s3:::other-bucket"]);
  assertEquals(applyFilters(ARNS, "", new Set(["s3", "lambda"])).length, 3);
});
