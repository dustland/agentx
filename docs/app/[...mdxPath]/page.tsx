import { generateStaticParamsFor, importPage } from "nextra/pages";
import type { FC } from "react";
import { useMDXComponents as getMDXComponents } from "../../mdx-components";

export async function generateStaticParams() {
  const params = await generateStaticParamsFor("mdxPath")();
  return params;
}

export async function generateMetadata(props: PageProps) {
  const params = await props.params;
  const { metadata } = await importPage(params.mdxPath || []);
  return metadata;
}

type PageProps = Readonly<{
  params: Promise<{
    mdxPath?: string[];
  }>;
}>;

const Wrapper = getMDXComponents({}).wrapper!;

const Page: FC<PageProps> = async (props) => {
  const params = await props.params;
  const result = await importPage(params.mdxPath || []);
  const { default: MDXContent, toc, metadata } = result;

  // Check if this is an API page
  const isApiPage = params.mdxPath && params.mdxPath[0] === "api";

  return (
    <Wrapper toc={toc} metadata={metadata}>
      <div className={isApiPage ? "api-page" : ""}>
        <MDXContent {...props} params={params} />
      </div>
    </Wrapper>
  );
};

export default Page;
