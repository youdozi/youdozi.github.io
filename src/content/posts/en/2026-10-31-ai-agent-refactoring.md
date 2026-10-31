---
kind: "post"
publishedAt: "2026-10-31T15:07:08.634155+00:00"
updatedAt: "2026-10-31T15:07:08.634155+00:00"
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Self-reviewed English translation of the Korean guide; Java 21 initial/refactored examples and one boundary mutation executed. Localized diagram checked. Prompts are authored examples, not AI-product trial transcripts. No integration, productivity or performance benchmark."
reviewSources: ["https://refactoring.com/", "https://google.github.io/eng-practices/review/developer/small-cls.html", "https://docs.github.com/en/copilot/responsible-use/agents"]
language: "en"
translationKey: "2026-10-31-ai-agent-refactoring"
routeSlug: "2026-10-31-ai-agent-refactoring"
title: "Refactoring code with AI agents: preserving behavior and verifiable changes"
description: "Give AI agents a refactoring scope, behavior to preserve, and verification commands. Use before-and-after Java examples and prompts to examine boundaries, exceptions, change scope, and test reliability."
categories: ["architecture"]
tags: ["ai-agent", "refactoring", "java", "testing", "code-review", "developer-workflow"]
---

**Refactoring with an AI agent starts by defining the behavior to preserve and the scope to change, then checking the result through execution evidence and the diff.** A shorter function or an agent's claim that “tests passed” is not enough to call it complete. Check whether return values, exceptions, and external effects remain the same, and whether the verification itself has been weakened.

This is a tool-independent guide for developers familiar with Git and running tests. It assumes no particular product interface or model. The prompts below are authored examples you can copy and adapt, not transcripts obtained from a particular product or performance measurements. Execution results for the Java example are identified separately.

## What should the first request include?

[Martin Fowler defines refactoring](https://refactoring.com/) as changing internal structure while preserving externally observable behavior. If a policy change or bug fix is needed, distinguish it from refactoring so you can assess differences between the before and after results.

Give the agent not only the target files, but also callers, related tests, repository conventions, and actual verification commands. Rather than asking it to read the entire repository unconditionally, begin with the paths needed for this decision. Having it describe current behavior and supporting evidence without editing files first can reduce the risk of changes expanding from a misunderstanding.

The shipping policy in the example below consists of the following **requirements defined for illustration**. It is not an actual service policy or incident report.

| Condition | Behavior to preserve |
| --- | --- |
| Negative order subtotal | Throw `IllegalArgumentException("subtotal")` |
| Member or order subtotal of at least 50,000 KRW | Base shipping fee of 0 KRW |
| Otherwise | Base shipping fee of 3,000 KRW |
| Delivery to an island or remote area | Add 3,000 KRW regardless of whether base shipping is free |

You can write the first request to the agent as follows. Assume the full code later in this article has been saved as `ShippingRefactorDemo.java`. To practice the editing process with an agent, first copy the body of `before()` into `after()`. The full code below includes the completed refactoring for comparison.

```text
Read before(), after(), and main() in ShippingRefactorDemo.java and analyze only.
Do not modify files yet.

Goal: reduce nested branches in after() while preserving the shipping-fee behavior of before().
Input amounts are in KRW and use long.
Check the exception type and message for negative amounts, the 50,000 KRW boundary,
and combinations of free base shipping and the remote-area surcharge.

Provide code evidence for the current behavior, the test scope already covered,
additional boundary cases to check, and a minimal change that modifies only after().
Do not guess and change unclear policies.
```

The useful result at this stage is current behavior for each condition and the locations to change, rather than an abstract “code quality improvement plan.” For example, an interpretation that “members always pay 0 KRW for shipping” conflicts with the remote-area surcharge and should be corrected before implementation.

## Make a small change and compare behavior

This example **separates base shipping and surcharge calculations** from duplicated branches. It preserves existing inputs, outputs, and exceptions without adding a strategy interface or configuration layer. A small change lets reviewers focus on whether only structure changed while policy stayed the same. [Google's guidance on small changes](https://google.github.io/eng-practices/review/developer/small-cls.html)

![Throw the same exception for a negative subtotal, calculate base shipping from membership and the free-shipping threshold, then add the remote-area surcharge and return the total](/assets/img/architecture/ai-agent-refactoring-en.svg)

The diagram shows the calculation order in `after()` below. It does not depict the internals of an AI tool. `before()` and `after()` were written for illustration; `main()` checks explicit expected values and compares their results. It runs on JDK 21 or later without external dependencies.

```java
public class ShippingRefactorDemo {
    static final long FREE_THRESHOLD = 50_000;
    record Case(long subtotal, boolean member, boolean remote, long expected) {}

    static long before(long subtotal, boolean member, boolean remote) {
        if (subtotal < 0) throw new IllegalArgumentException("subtotal");
        if (member) {
            if (remote) return 3_000;
            return 0;
        }
        if (subtotal >= 50_000) {
            if (remote) return 3_000;
            return 0;
        }
        if (remote) return 6_000;
        return 3_000;
    }

    static long after(long subtotal, boolean member, boolean remote) {
        if (subtotal < 0) throw new IllegalArgumentException("subtotal");
        long base = (member || subtotal >= FREE_THRESHOLD) ? 0 : 3_000;
        long surcharge = remote ? 3_000 : 0;
        return base + surcharge;
    }

    static void equal(long actual, long expected) {
        if (actual != expected) {
            throw new AssertionError("expected=" + expected + ", actual=" + actual);
        }
    }

    public static void main(String[] args) {
        Case[] examples = {
            new Case(0, false, false, 3_000),
            new Case(49_999, false, false, 3_000),
            new Case(50_000, false, false, 0),
            new Case(0, true, false, 0),
            new Case(49_999, false, true, 6_000),
            new Case(50_000, false, true, 3_000),
            new Case(0, true, true, 3_000),
            new Case(Long.MAX_VALUE, false, true, 3_000)
        };
        for (Case c : examples) {
            equal(before(c.subtotal(), c.member(), c.remote()), c.expected());
            equal(after(c.subtotal(), c.member(), c.remote()), c.expected());
        }
        System.out.println("examples=" + examples.length);

        int comparisons = 0;
        long[] amounts = {0, 1, 49_999, 50_000, 50_001, Long.MAX_VALUE};
        for (long subtotal : amounts) {
            for (boolean member : new boolean[] {false, true}) {
                for (boolean remote : new boolean[] {false, true}) {
                    equal(after(subtotal, member, remote), before(subtotal, member, remote));
                    comparisons++;
                }
            }
        }
        System.out.println("comparisons=" + comparisons);

        int rejected = 0;
        for (boolean refactored : new boolean[] {false, true}) {
            try {
                if (refactored) after(-1, false, false);
                else before(-1, false, false);
                throw new AssertionError("Negative amount was accepted");
            } catch (IllegalArgumentException e) {
                if (!"subtotal".equals(e.getMessage())) throw new AssertionError(e);
                rejected++;
            }
        }
        System.out.println("negative-inputs=" + rejected);
    }
}
```

```sh
javac --release 21 ShippingRefactorDemo.java
java ShippingRefactorDemo
```

The following output was obtained with Zulu JDK `21.0.1+12-LTS`. Both the initial version, with the same body in `after()` and `before()`, and the completed refactoring below produced this output.

```text
examples=8
comparisons=24
negative-inputs=2
```

Instead of Java `assert`, which can be disabled depending on the `-ea` option, the code directly throws `AssertionError` when it finds a difference. The reported counts are the numbers of specified cases and input combinations; they do not represent coverage of an entire production codebase.

When requesting implementation, connect the previously verified conditions to the editing scope and execution commands.

```text
Refactor only after(), preserving the shipping contract established above.
Do not change before(), main(), expected values, or FREE_THRESHOLD.
Preserve public inputs and outputs and exception types and messages; add no dependencies or new layers.
If you think changes outside this file are needed, explain the reasons without applying them.

Run javac --release 21 ShippingRefactorDemo.java and java ShippingRefactorDemo.
Provide the commands actually run, exit codes, observed output, and change diff.
If a check fails, narrow down and fix the failing condition and cause; do not delete checks or adjust expected values to make it pass.
```

If the agent's environment cannot edit files or run commands, apply the proposed patch yourself and run the same commands. “Do not change” in a prompt communicates work scope; it does not replace actual tool permissions or file-access restrictions.

## Are passing tests and preserved behavior the same thing?

This example checks 8 explicit expected values, compares before-and-after results for 24 input combinations, and checks the exceptions from both methods for negative inputs. It is not a proof of equivalence for every `long` input. Using only the result of `before()` as the answer can preserve existing defects, so use independent expected values and business requirements as well. If you discover an existing defect, decide separately whether to fix it and which behavior will change.

You can also introduce a counterexample to see whether verification catches a relevant difference. For example, changing `subtotal >= FREE_THRESHOLD` in `after()` to `subtotal > FREE_THRESHOLD` excludes nonmember orders of exactly 50,000 KRW from free base shipping. The expected-value check should then fail.

Running a temporary copy with only that boundary condition incorrectly changed was verified to fail with `AssertionError: expected=0, actual=3000`. This confirms that the checks detect one particular error; it does not guarantee detection of every incorrect change. That mutation is not applied to the completed code in this article.

In a real project, check caller-observable behavior beyond return values: exceptions, DB queries and transaction boundaries, external-call counts and ordering, serialized results, and resource release. Passing this pure-function example does not verify DB or HTTP paths. If performance improvement is the goal, separate measurements with fixed inputs and environment are also needed.

## Start the final review with the changes, before the explanation

Inspect the diff and execution results before reading the agent's change description. Look for unnecessary file changes, deleted or skipped tests, swallowed exceptions, and dependencies unrelated to the feature. `git diff --check` checks whitespace errors and similar issues; it is not a test of business behavior.

If a separate review context is available, provide the original requirements, before-and-after code, diff, and execution evidence rather than the initial claim of success. Reviews can also produce incorrect findings, so compare each comment against evidence in the code and requirements. [GitHub's documentation on agent limitations](https://docs.github.com/en/copilot/responsible-use/agents) also explains that generated code and review comments can be inaccurate.

```text
Review this change without modifying it.
Input: shipping-fee requirements, before-and-after code, diff, test commands, and actual results.

Find counterexamples that change return values, exceptions, the 50,000 KRW boundary, or remote-area fees.
Also check for changes outside scope and weakened tests.
For each finding, give its location, an example input, the observable difference, and supporting evidence.
Do not claim to have run checks you did not execute.
```

Keep the final handoff brief: describe the changed structure, preserved behavior, checks actually run, and remaining verification scope. If a test fails, strengthen the failing input and expected behavior, then narrow the fix again; if changes grow, split them into separate work. **A change small enough for a reviewer to explain why behavior is preserved** remains a useful unit of completion when working with AI agents.
