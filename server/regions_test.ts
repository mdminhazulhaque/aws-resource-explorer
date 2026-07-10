import { assertEquals } from "@std/assert";
import { AWS_REGIONS } from "./regions.ts";

Deno.test("AWS_REGIONS has 17 entries in 'code (Name)' format", () => {
  assertEquals(AWS_REGIONS.length, 17);
  assertEquals(AWS_REGIONS[0], "us-east-1 (N. Virginia)");
  for (const region of AWS_REGIONS) {
    assertEquals(/^[a-z]{2}-[a-z]+-\d \(.+\)$/.test(region), true, region);
  }
});
