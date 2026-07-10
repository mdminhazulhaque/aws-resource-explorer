import { assertEquals } from "@std/assert";
import { listProfiles } from "./aws.ts";

Deno.test("listProfiles merges and sorts config + credentials profiles", async () => {
  const dir = await Deno.makeTempDir();
  await Deno.writeTextFile(
    `${dir}/config`,
    "[profile alpha]\nregion = us-east-1\n\n[profile beta]\nregion = us-west-2\n",
  );
  await Deno.writeTextFile(
    `${dir}/credentials`,
    "[beta]\naws_access_key_id = x\n\n[gamma]\naws_access_key_id = y\n",
  );
  const profiles = await listProfiles({
    configFilepath: `${dir}/config`,
    filepath: `${dir}/credentials`,
  });
  assertEquals(profiles, ["alpha", "beta", "gamma"]);
});

Deno.test("listProfiles returns empty array when files are missing", async () => {
  const dir = await Deno.makeTempDir();
  const profiles = await listProfiles({
    configFilepath: `${dir}/none`,
    filepath: `${dir}/none2`,
  });
  assertEquals(profiles, []);
});
