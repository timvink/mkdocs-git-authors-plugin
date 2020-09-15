# Aggregating Authors

In some repositories authors may have committed with differing name/email combinations.
In order to prevent the output being split it is possible to aggregate authors on
arbitrary elements by providing a file `.mailmap` in the repository's root directory.
This is a feature of Git itself. The following example will aggregate the contributions
of Jane Doe committed under two email addresses:

```
# .mailmap
Jane Doe <jane.doe@company.com> <jane.doe@private-email.com>
```

This will map commits made with the `private-email.com` to the company address. For more details
and further options (e.g. mapping between different names or misspellings etc. see the
[git-blame documentation](https://git-scm.com/docs/git-blame#_mapping_authors).