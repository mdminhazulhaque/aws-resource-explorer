import { assertEquals } from "@std/assert";
import { listProfiles, loadResources, type TaggingClient } from "./aws.ts";

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

function stubClient(pages: { arns: string[]; nextToken?: string }[]): TaggingClient {
  let call = 0;
  return { getResources: () => Promise.resolve(pages[call++]) };
}

Deno.test("loadResources yields progress per page then done with all ARNs", async () => {
  const client = stubClient([
    { arns: ["arn:aws:s3:::bucket-a"], nextToken: "t1" },
    { arns: ["arn:aws:lambda:us-east-1:123:function:fn"], nextToken: undefined },
  ]);
  const events = [];
  for await (const event of loadResources(client)) events.push(event);
  assertEquals(events, [
    { type: "progress", count: 1 },
    { type: "progress", count: 2 },
    {
      type: "done",
      arns: ["arn:aws:s3:::bucket-a", "arn:aws:lambda:us-east-1:123:function:fn"],
    },
  ]);
});

Deno.test("loadResources yields error event when the client throws", async () => {
  const client: TaggingClient = {
    getResources: () => Promise.reject(new Error("The SSO session has expired")),
  };
  const events = [];
  for await (const event of loadResources(client)) events.push(event);
  assertEquals(events, [{ type: "error", message: "The SSO session has expired" }]);
});
