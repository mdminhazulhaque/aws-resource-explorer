import { loadSharedConfigFiles } from "@smithy/shared-ini-file-loader";
import {
  GetResourcesCommand,
  ResourceGroupsTaggingAPIClient,
} from "@aws-sdk/client-resource-groups-tagging-api";
import { fromIni } from "@aws-sdk/credential-providers";

export interface ProfileFilePaths {
  configFilepath?: string;
  filepath?: string;
}

export async function listProfiles(
  paths: ProfileFilePaths = {},
): Promise<string[]> {
  const { configFile, credentialsFile } = await loadSharedConfigFiles({
    ...paths,
    ignoreCache: true,
  });
  const names = new Set([
    ...Object.keys(configFile),
    ...Object.keys(credentialsFile),
  ]);
  return [...names].sort();
}

export interface ResourcePage {
  arns: string[];
  nextToken?: string;
}

export interface TaggingClient {
  getResources(paginationToken?: string): Promise<ResourcePage>;
}

export function createTaggingClient(
  profile: string,
  region: string,
): TaggingClient {
  const client = new ResourceGroupsTaggingAPIClient({
    region,
    credentials: fromIni({ profile }),
  });
  return {
    async getResources(paginationToken) {
      const response = await client.send(
        new GetResourcesCommand(
          paginationToken ? { PaginationToken: paginationToken } : {},
        ),
      );
      return {
        arns: (response.ResourceTagMappingList ?? [])
          .map((resource) => resource.ResourceARN)
          .filter((arn): arn is string => Boolean(arn)),
        nextToken: response.PaginationToken || undefined,
      };
    },
  };
}

export type LoadEvent =
  | { type: "progress"; count: number }
  | { type: "done"; arns: string[] }
  | { type: "error"; message: string };

export async function* loadResources(
  client: TaggingClient,
): AsyncGenerator<LoadEvent> {
  const arns: string[] = [];
  let token: string | undefined;
  try {
    do {
      const page = await client.getResources(token);
      arns.push(...page.arns);
      token = page.nextToken;
      yield { type: "progress", count: arns.length };
    } while (token);
    yield { type: "done", arns };
  } catch (error) {
    yield {
      type: "error",
      message: error instanceof Error ? error.message : String(error),
    };
  }
}
